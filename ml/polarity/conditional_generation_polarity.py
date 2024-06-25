# coding:utf-8
# import sys
#
# import torch
import os
# import numpy as np
# import evaluate
# import mlflow
# from sklearn.metrics import classification_report
#
# from transformers import DataCollatorForSeq2Seq, HfArgumentParser, EarlyStoppingCallback
# from transformers import Seq2SeqTrainingArguments, Seq2SeqTrainer, set_seed
# from transformers import T5Tokenizer, T5ForConditionalGeneration
#
# from trainer_seq2seq import ModelArguments, DataTrainingArguments, load_and_prepare_data

# mlflow server --host 0.0.0.0 --port 8080

os.environ["MLFLOW_EXPERIMENT_NAME"] = "polarity_classif"
os.environ["MLFLOW_FLATTEN_PARAMS"] = "1"
os.environ["MLFLOW_TRACKING_URI"]=""
os.environ["HF_MLFLOW_LOG_ARTIFACTS"]="1"

def main():
    with open('models' + os.sep + 'mytest.txt', "w") as writer:
        writer.write("index\ttext\tgold\tprediction\ncoucouuuuuuuuuuuuuu")
    # parser = HfArgumentParser((ModelArguments, DataTrainingArguments, Seq2SeqTrainingArguments ))
    # model_args, data_args, training_args = parser.parse_json_file(json_file=os.path.abspath(sys.argv[1]))
    #
    # set_seed(training_args.seed)
    #
    # if not training_args.no_cuda and torch.cuda.is_available():
    #     device = "cuda"
    # else:
    #     device = "cpu"
    # label2id = {'negative': 0, 'neutral': 1, 'positive': 2}
    # id2label = {0: 'negative', 1: 'neutral', 2: 'positive'}
    #
    # tokenizer = T5Tokenizer.from_pretrained(model_args.tokenizer_name if model_args.tokenizer_name else model_args.model_name_or_path)
    #
    # f1_score = evaluate.load("f1")


    # def preprocess_function(examples):
    #     inputs = ["Is this text about " + entity + " is 'neutral', 'positive' or 'negative' ? text : " + doc for
    #               doc, entity in list(zip(examples[data_args.text_column_name], examples['entity']))]
    #     model_inputs = tokenizer(inputs, max_length=200, truncation=True)
    #     labels = tokenizer(text_target=examples[data_args.label_column_name], max_length=8, truncation=True)
    #     model_inputs["labels"] = labels["input_ids"]
    #     return model_inputs
    #
    # def compute_metrics(eval_pred):
    #
    #     preds, labels = eval_pred
    #     labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
    #
    #     decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=model_args.skip_special_tokens)
    #     decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=model_args.skip_special_tokens)
    #
    #     id_decoded_preds = [label2id[x] if x in label2id else 1 for x in decoded_preds]
    #     id_decoded_labels = [label2id[x] if x in label2id else 1 for x in decoded_labels]
    #     result = f1_score.compute(predictions=id_decoded_preds, references=id_decoded_labels, average='macro')
    #     print(classification_report(id_decoded_labels, id_decoded_preds))
    #     return {k: round(v, 4) for k, v in result.items()}

    # # load data
    # data = load_and_prepare_data(data_args.input_dir,
    #                              data_args.input_file,
    #                              data_args.text_column_name,
    #                              data_args.label_column_name,
    #                              data_args.extract_from_mongodb,
    #                              data_args.add_data_augmentation)
    #
    # tokenized_data = data.map(preprocess_function, batched=True)
    #
    # model = T5ForConditionalGeneration.from_pretrained(model_args.model_name_or_path)
    # model.to(device)
    #
    # data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model)
    # trainer = Seq2SeqTrainer(
    #     model=model,
    #     args=training_args,
    #     train_dataset=tokenized_data["train"],
    #     eval_dataset=tokenized_data["dev"],
    #     tokenizer=tokenizer,
    #     data_collator=data_collator,
    #     compute_metrics=compute_metrics,
    #     callbacks=[EarlyStoppingCallback(early_stopping_patience=1)]
    # )
    #
    # if training_args.do_train:
    #     train_results = trainer.train()
    #     mlflow.end_run()
    #     trainer.save_model('..' + os.sep + 'models' + os.sep + training_args.output_dir)
    #     metrics = train_results.metrics
    #     trainer.log_metrics("train", metrics)
    #     trainer.save_metrics("train", metrics)
    #
    # # Evaluate the fine-tuned model
    # if training_args.do_eval:
    #     print("---- Evaluate ----")
    #     metrics = trainer.evaluate()
    #     trainer.log_metrics("dev", metrics)
    #     trainer.save_metrics("dev", metrics)
    #
    # # Predict on test set
    # if training_args.do_predict:
    #     print("---- Predict ----")
    #     gold = tokenized_data['test']["labels"]
    #     res = trainer.predict(tokenized_data['test'], metric_key_prefix="predict")
    #     predictions = res.predictions
    #     dec_preds = tokenizer.batch_decode(predictions, skip_special_tokens=True)
    #     dec_labels = tokenizer.batch_decode(gold, skip_special_tokens=True)
    #
    #     trainer.log_metrics("test", res.metrics)
    #     trainer.save_metrics("test", res.metrics)
    #     test_predictions_file = os.path.join(training_args.output_dir, "predictions.txt")
    #     if trainer.is_world_process_zero():
    #         with open(test_predictions_file, "w") as writer:
    #             print("---- Predict results ----")
    #             writer.write("index\ttext\tgold\tprediction\n")
    #             for index, item in enumerate(dec_preds):
    #                 g = dec_labels[index]
    #                 text = tokenized_data['test'][index]['text']
    #                 if g!=item:
    #                     print(f"{index}\t{text}\t{g}\t{item}\n")
    #                 writer.write(f"{index}\t{text}\t{g}\t{item}\n")


if __name__ == '__main__':
    main()
