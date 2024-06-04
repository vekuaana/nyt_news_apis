import nltk
import os
import torch
import mlflow
import sys
from torch import nn
import numpy as np
from huggingface_hub import HfFolder
from sklearn.metrics import precision_recall_fscore_support
from transformers import (
    AutoConfig,
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    set_seed
)

from transformers import DataCollatorForSeq2Seq, HfArgumentParser, DataCollatorWithPadding
from transformers import AutoTokenizer
from transformers import EarlyStoppingCallback, IntervalStrategy, GenerationConfig
from transformers.optimization import Adafactor, AdafactorSchedule
from sklearn.metrics import classification_report
from trainer_seq2seq import ModelArguments, DataTrainingArguments, load_and_prepare_data

os.environ["MLFLOW_EXPERIMENT_NAME"] = "polarity"
os.environ["MLFLOW_FLATTEN_PARAMS"] = "1"


def compute_metrics(eval_pred) -> dict:
    """Compute metrics for evaluation"""
    logits, labels = eval_pred

    if isinstance(logits, tuple):  # if the model also returns hidden_states or attentions
        print("\n--------------")
        logits = logits[0]
    predictions = np.argmax(logits, axis=-1)
    print(logits)
    print(nn.functional.softmax(torch.tensor(logits), dim=0))
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, predictions, average="macro"
    )
    print(classification_report(labels, predictions))
    return {"precision": precision, "recall": recall, "f1": f1}


def main() -> None:

    parser = HfArgumentParser((ModelArguments, DataTrainingArguments, TrainingArguments))
    model_args, data_args, training_args = parser.parse_json_file(json_file=os.path.abspath(sys.argv[1]))

    set_seed(training_args.seed)

    label2id = {'negative': 0, 'neutral': 1, 'positive': 2}
    id2label = {0: 'negative', 1: 'neutral', 2: 'positive'}

    config = AutoConfig.from_pretrained(
        model_args.model_name_or_path, num_labels=len(label2id), id2label=id2label, label2id=label2id
    )

    if not training_args.no_cuda and torch.cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"
    print(device)

    model = AutoModelForSequenceClassification.from_pretrained(model_args.model_name_or_path, config=config).to(device)
    tokenizer = AutoTokenizer.from_pretrained(model_args.model_name_or_path)

    def tokenize_function(examples) -> dict:
        """Tokenize the text column in the dataset"""
        examples["text"] = ["Is this text about " + entity + " is 'neutral', 'positive' or 'negative'  : " + doc for
                            doc, entity in list(zip(examples['text'], examples['entity']))]
        return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=200)

    dataset = load_and_prepare_data(data_args.input_dir,
                             data_args.input_file,
                             data_args.text_column_name,
                             data_args.label_column_name,
                             data_args.extract_from_mongodb,
                             data_args.add_data_augmentation,
                             'sequence_classification')

    tokenized_datasets = dataset.map(tokenize_function, batched=True)
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["dev"],
        compute_metrics=compute_metrics,
        data_collator=data_collator
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
        gold = tokenized_datasets['test']["labels"]
        res = trainer.predict(tokenized_datasets['test'], metric_key_prefix="predict")
        logits = res.predictions[0]
        predictions = np.argmax(logits, axis=-1)
        print(nn.functional.softmax(torch.tensor(logits), dim=0))

        # trainer.log_metrics("test", res.metrics)
        # trainer.save_metrics("test", res.metrics)
        test_predictions_file = os.path.join(training_args.output_dir, "predictions.txt")
        if trainer.is_world_process_zero():
            with open(test_predictions_file, "w") as writer:
                print("---- Predict results ----")
                writer.write("index\ttext\tentity\tgold\tprediction\n")
                for index, item in enumerate(predictions):
                    g = gold[index]
                    entity = tokenized_datasets['test'][index]['entity']
                    text = tokenized_datasets['test'][index]['text']
                    if g != item:
                        print(f"{index}\t{text}\t{entity}\t{g}\t{item}\n")
                    writer.write(f"{index}\t{text}\t{entity}\t{g}\t{item}\n")


if __name__ == '__main__':
    # get_polarity = pipeline("text2text-generation", model="t5_base_10epochs")
    # pred = get_polarity(
    #     "Is this text about Sanders is 'neutral', 'positive' or 'negative' ? text :  Buttigieg soars, Biden slips, Sanders still on top in newest New Hampshire poll")
    # print(pred)
    # pred = get_polarity(
    #     "Is this text about Biden is 'neutral', 'positive' or 'negative' ? text :  Buttigieg soars, Biden slips, Sanders still on top in newest New Hampshire poll")
    # print(pred)

    main()

