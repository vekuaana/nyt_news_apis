# coding:utf-8
import logging
import sys

import torch
import os
import pandas as pd
import numpy as np
import evaluate
import mlflow

from transformers import DataCollatorForSeq2Seq, HfArgumentParser
from transformers import AutoTokenizer
from transformers import AutoModelForSeq2SeqLM, Seq2SeqTrainingArguments, Seq2SeqTrainer, set_seed
from transformers import pipeline

from trainer_seq2seq import ModelArguments, DataTrainingArguments, load_and_prepare_data
# base on https://www.dialog-21.ru/media/5916/moloshnikoviplusetal113.pdf
# exemple qui focntionne en changeant Sanders par Biden : Is this text about Sanders is 'neutral', 'positive' or 'negative' ? text :  Buttigieg soars, Biden slips, Sanders still on top in newest New Hampshire poll

os.environ["MLFLOW_EXPERIMENT_NAME"] = "polarity-classification"
os.environ["MLFLOW_FLATTEN_PARAMS"] = "1"


def main():
    parser = HfArgumentParser((ModelArguments, DataTrainingArguments, Seq2SeqTrainingArguments ))
    model_args, data_args, training_args = parser.parse_json_file(json_file=os.path.abspath(sys.argv[1]))

    # params
    set_seed(training_args.seed) # Set seed before initializing model.

    if not training_args.no_cuda and torch.cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"

    label2id = {'negative': 0, 'neutral': 1, 'positive': 2}

    tokenizer = AutoTokenizer.from_pretrained(model_args.tokenizer_name if model_args.tokenizer_name else model_args.model_name_or_path)
    f1_score = evaluate.load("f1")

    def preprocess_function(examples):
        inputs = ["Is this text about " + entity + " is 'neutral', 'positive' or 'negative' ? text : " + doc for
                  doc, entity in list(zip(examples[data_args.text_column_name], examples['entity']))]
        # inputs = ["what is the feeling associated with this text about " + entity + " between 'neutral', 'positive' and 'negative': " + doc
        # for doc, entity in list(zip(examples[data_args.text_column_name], examples['entity']))]
        model_inputs = tokenizer(inputs, max_length=200, truncation=True)
        labels = tokenizer(text_target=examples[data_args.label_column_name], max_length=10, truncation=True)
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    def compute_metrics(eval_pred):

        preds, labels = eval_pred
        decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=model_args.skip_special_tokens)
        labels = np.where(labels != -100, labels, tokenizer.pad_token_id)

        decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=model_args.skip_special_tokens)

        id_decoded_preds = [label2id[x] if x in label2id else 1 for x in decoded_preds]
        id_decoded_labels = [label2id[x] if x in label2id else 1 for x in decoded_labels]
        result = f1_score.compute(predictions=id_decoded_preds, references=id_decoded_labels, average='macro')

        return {k: round(v, 4) for k, v in result.items()}

    # load data
    data = load_and_prepare_data(data_args.input_dir,
                                 data_args.input_file,
                                 data_args.text_column_name,
                                 data_args.label_column_name,
                                 data_args.extract_from_mongodb)

    tokenized_data = data.map(preprocess_function, batched=True)

    model = AutoModelForSeq2SeqLM.from_pretrained(model_args.model_name_or_path)
    model.to(device)
    data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model)

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_data["train"],
        eval_dataset=tokenized_data["dev"],
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
    )

    if training_args.do_train:
        train_results = trainer.train()
        mlflow.end_run()
        trainer.save_model(training_args.output_dir)
        metrics = train_results.metrics
        trainer.log_metrics("train", metrics)
        trainer.save_metrics("train", metrics)

    # Evaluate the fine-tuned model
    if training_args.do_eval:
        print("---- Evaluate ----")
        metrics = trainer.evaluate()
        trainer.log_metrics("dev", metrics)
        trainer.save_metrics("dev", metrics)

    # Predict on test set
    if training_args.do_predict:
        print("---- Predict ----")
        gold = tokenized_data['test']["labels"]
        res = trainer.predict(tokenized_data['test'], metric_key_prefix="predict")
        predictions = res.predictions
        dec_preds = tokenizer.batch_decode(predictions, skip_special_tokens=True)
        dec_labels = tokenizer.batch_decode(gold, skip_special_tokens=True)

        trainer.log_metrics("test", res.metrics)
        trainer.save_metrics("test", res.metrics)
        test_predictions_file = os.path.join(training_args.output_dir, "predictions.txt")
        if trainer.is_world_process_zero():
            with open(test_predictions_file, "w") as writer:
                print("---- Predict results ----")
                writer.write("index\ttext\tentity\tgold\tprediction\n")
                for index, item in enumerate(dec_preds):
                    g = dec_labels[index]
                    entity = tokenized_data['test'][index]['entity']
                    text = tokenized_data['test'][index]['text']
                    if g!=item:
                        print(f"{index}\t{text}\t{entity}\t{g}\t{item}\n")
                    writer.write(f"{index}\t{text}\t{entity}\t{g}\t{item}\n")


if __name__=='__main__':
    # get_polarity = pipeline("text2text-generation", model="t5_base_10epochs")
    # pred = get_polarity(
    #     "Is this text about Sanders is 'neutral', 'positive' or 'negative' ? text :  Buttigieg soars, Biden slips, Sanders still on top in newest New Hampshire poll")
    # print(pred)
    # pred = get_polarity(
    #     "Is this text about Biden is 'neutral', 'positive' or 'negative' ? text :  Buttigieg soars, Biden slips, Sanders still on top in newest New Hampshire poll")
    # print(pred)

    main()
