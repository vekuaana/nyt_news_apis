# coding:utf-8

import os
import pandas as pd

from dotenv import load_dotenv, find_dotenv
from typing import Optional, Union
from dataclasses import dataclass, field
from datasets import Dataset, DatasetDict

from sklearn.model_selection import train_test_split

from pymongo import MongoClient
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError


load_dotenv(find_dotenv())

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
            "help": "Whether to skip special tokens when decoding."
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
    extract_from_mongodb: Optional[bool] = field(
        default=False,
        metadata={"help": "Whether to use MongoDB dataset"},
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


def get_db(host):
    """
        Connect to the MongoDB instance and return the database object.

        Args:
            host (str): 'localhost' or 'mongodb' (container name)

        Returns:
            mongodb: The database object if the connection is successful.
        """

    try:
        client = MongoClient(host=host,
                             port=27017,
                             username=os.getenv('USER1'),
                             password=os.getenv('PASSWORD1'),
                             authSource=os.getenv('MONGO_INITDB_DATABASE'))

        client.server_info()
        mongodb = client[os.getenv('MONGO_INITDB_DATABASE')]
        return mongodb
    except OperationFailure as of:
        print(of)


def read_data_from_mongo(collection, query={}, no_id=True):
    """ Read from Mongo and Store into DataFrame """

    def extract_data(db):
        # Make a query to the specific DB and Collection
        cursor = db[collection].find(query)

        # Expand the cursor and construct the DataFrame
        df = pd.DataFrame(list(cursor))

        # Delete the _id
        if no_id:
            del df['_id']

        return df
    try:
        # Attempt to connect to MongoDB within a container environment
        db_nyt_news = get_db('mongodb')
        return extract_data(db_nyt_news)
    except ServerSelectionTimeoutError:
        # Handle the case where the connection times out if we try to connect outside the container
        print("Try to connect outside the container with localhost")
        db_nyt_news = get_db('localhost')
        return extract_data(db_nyt_news)
    except OperationFailure as of:
        print(of)
        return None


def load_and_prepare_data(data_dir: str, path: str, text_col: str, label_col: str, use_mongodb: bool) -> DatasetDict:
    """
    Load and prepare dataset for training  (train), validation (dev), and testing (test).

    Args:
        data_dir (str): path to directory where the dataset file is located.
        path (str): filename of the dataset.
        text_col (str): name of the column containing the text data.
        label_col (str): name of the column containing the labels.
        use_mongodb (bool): whether to use the MongoDB dataset

    Returns:
        DatasetDict: A dictionary containing the train, dev and test datasets.
    """
    if not use_mongodb:
        df = pd.read_csv(data_dir + os.sep + path, sep=',', encoding='utf-8')
    else:
        df = read_data_from_mongo('polarity_dataset')
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
