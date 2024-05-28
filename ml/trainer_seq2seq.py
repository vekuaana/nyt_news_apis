# coding:utf-8

import os
import pandas as pd

from typing import Optional, Union
from dataclasses import dataclass, field
from datasets import Dataset, DatasetDict

from sklearn.model_selection import train_test_split


@dataclass
class ModelArguments:

    model_name_or_path: str = field(
        metadata={"help": "Path to pretrained model or model identifier from huggingface.co/models"}
    )
    config_name: Optional[str] = field(
        default=None, metadata={"help": "Pretrained config name or path if not the same as model_name"}
    )
    tokenizer_name: Optional[str] = field(
        default=None, metadata={"help": "Pretrained tokenizer name or path if not the same as model_name"}
    )
    skip_special_tokens: bool = field(
        default=True,
        metadata={
            "help": "Wheter to skip special tokens when decoding."
        }
    )
    max_new_tokens: bool = field(
        default=1,
        metadata={
            "help": "Max new token to generate in decoder part"
        }
    )


@dataclass
class DataTrainingArguments:

    input_file: Optional[Union[list, str]] = field(
        default=None, metadata={"help": "The input data file or list of input data files."}
    )
    input_dir: Optional[str] = field(
        default=None,
        metadata={"help": "The path to input data directory."},
    )
    text_column_name: Optional[str] = field(
        default='text', metadata={"help": "The column name of text to input in the csv file."}
    )
    label_column_name: Optional[str] = field(
        default='labels', metadata={"help": "The column name of label to input in the csv file."}
    )
    overwrite_cache: bool = field(
        default=False, metadata={"help": "Overwrite the cached training and evaluation sets"}
    )
    max_source_length: Optional[int] = field(
        default=200,
        metadata={
            "help": "The maximum total input sequence length after tokenization."
        },
    )
    max_target_length: Optional[int] = field(
        default=8,
        metadata={
            "help": "The maximum total sequence length for target text after tokenization."
        },
    )
    val_max_target_length: Optional[int] = field(
        default=8,
        metadata={
            "help": "The maximum total sequence length for validation target text after tokenization."
        },
    )
    pad_to_max_length: bool = field(
        default=True,
    )
    max_train_samples: Optional[int] = field(
        default=None,
        metadata={
            "help": (
                "For debugging purposes or quicker training, truncate the number of training examples to this "
                "value if set."
            )
        },
    )
    max_eval_samples: Optional[int] = field(
        default=None,
        metadata={
            "help": (
                "For debugging purposes or quicker training, truncate the number of evaluation examples to this "
                "value if set."
            )
        },
    )
    max_predict_samples: Optional[int] = field(
        default=None,
        metadata={
            "help": (
                "For debugging purposes or quicker training, truncate the number of prediction examples to this "
                "value if set."
            )
        },
    )


def load_and_prepare_data(data_dir: str, path: str, text_col: str, label_col: str) -> DatasetDict:
    """
    Load and prepare dataset for training  (train), validation (dev), and testing (test).

    Args:
        data_dir (str): path to directory where the dataset file is located.
        path (str): filename of the dataset.
        text_col (str): name of the column containing the text data.
        label_col (str): name of the column containing the labels.

    Returns:
        DatasetDict: A dictionary containing the train, dev and test datasets.
    """
    df = pd.read_csv(data_dir + os.sep + path, sep=',', encoding='utf-8')
    df = df[df[label_col] != 'UNK']
    df["text"] = df[text_col]
    df[label_col] = [x.lower() for x in df[label_col]]

    train_temp, test = train_test_split(df, test_size=0.2, random_state=15)
    train, dev = train_test_split(train_temp, test_size=0.2, random_state=15)

    train_dataset = Dataset.from_pandas(train)
    dev_dataset = Dataset.from_pandas(dev)
    test_dataset = Dataset.from_pandas(test)

    datasets = DatasetDict()
    datasets['train'] = train_dataset
    datasets['test'] = test_dataset
    datasets['dev'] = dev_dataset

    return datasets
