# coding:utf-8

import os
import re
import random
import pandas as pd

from dotenv import load_dotenv, find_dotenv
from typing import Optional, Union
from dataclasses import dataclass, field
from datasets import Dataset, DatasetDict

from transformers import T5ForConditionalGeneration, AutoTokenizer

from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle

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
    add_data_augmentation: Optional[bool] = field(
        default=False,
        metadata={"help": "Whether to apply data augmentation"},
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


def get_db(host: str):
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


def read_data_from_mongo(collection: str, query={}, no_id: bool = True):
    """
    Read from MongoDB and store the result into df

    Args:
        collection (str): name of the MongoDB collection
        query (Dict[str, Any]): the MongoDB query to execute
        no_id (bool): Whether to exclude the '_id' field from df
    """

    def extract_data(db):
        cursor = db[collection].find(query)
        df = pd.DataFrame(list(cursor))

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


def load_and_prepare_data(data_dir: str,
                          path: str,
                          text_col: str,
                          label_col: str,
                          use_mongodb: bool,
                          add_data_augmentation: bool,
                          task: str = 'text2text') -> DatasetDict:
    """
    Load and prepare dataset for training  (train), validation (dev), and testing (test).

    Args:
        data_dir (str): path to directory where the dataset file is located.
        path (str): filename of the dataset.
        text_col (str): name of the column containing the text data.
        label_col (str): name of the column containing the labels.
        use_mongodb (bool): whether to use the MongoDB dataset
        add_data_augmentation (bool): whether to add data augmentation for positive text
        task (str): two values -> 'sequence_classification' or 'text2text'. If 'sequence_classification', convert labels to ids

    Returns:
        DatasetDict: A dictionary containing the train, dev and test datasets.
    """
    if not use_mongodb:
        df = pd.read_csv(data_dir + os.sep + path, sep=',', encoding='utf-8')

    else:
        try:
            df = read_data_from_mongo('polarity_dataset')
        except ServerSelectionTimeoutError:
            df = pd.read_csv(data_dir + os.sep + path, sep=',', encoding='utf-8')

    df["text"] = df[text_col]
    df[label_col] = [x.lower() for x in df[label_col]]

    if task == "sequence_classification":
        df['labels'] = [0 if x == 'negative' else 1 if x == 'neutral' else 2 for x in df[label_col]]

    train, test_tmp = train_test_split(df, test_size=0.2, random_state=78)
    test, dev = train_test_split(test_tmp, test_size=0.5, random_state=72)

    if add_data_augmentation:
        train = apply_data_augmentation(train, label_col)

    train_dataset = Dataset.from_pandas(train)
    dev_dataset = Dataset.from_pandas(dev)
    test_dataset = Dataset.from_pandas(test)

    datasets = DatasetDict()
    datasets['train'] = train_dataset
    datasets['test'] = test_dataset
    datasets['dev'] = dev_dataset

    return datasets


def apply_data_augmentation(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """
    Apply data augmentation by back-translating on positive examples.
    Replace entities with random names.

    Args:
        df (DataFrame): The train DataFrame containing the data.
        col (str): The column name to filter positive examples.

    Returns:
        DataFrame: The augmented DataFrame.
    """
    back_translator = BackTranslator()
    positive_examples = df[df[col] == 'positive']
    shuffled_examples = shuffle(positive_examples, random_state=5).head(80)

    shuffled_examples['text'] = shuffled_examples['text'].apply(back_translator.back_translate)

    shuffled_examples['entity_present'] = shuffled_examples.apply(
        lambda row: row['entity'] in row['text'], axis=1
    )
    valid_examples = shuffled_examples[shuffled_examples['entity_present']].copy()

    names = ["Smith", "Davis", "Garcia", "Lopez", "Anderson", "Ramirez", "CampBell", "Mitchell"]
    valid_examples['old_entity'] = valid_examples['entity']
    valid_examples['entity'] = valid_examples['entity'].apply(lambda x: random.choice(names))
    valid_examples['text'] = valid_examples.apply(
        lambda row: re.sub(re.escape(row['old_entity']), row['entity'], row['text']),
        axis=1
    )

    valid_examples.drop(columns=['entity_present', 'old_entity'], inplace=True)
    augmented_df = shuffle(pd.concat([df, valid_examples], ignore_index=True))

    return augmented_df


class BackTranslator:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
        self.model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-base", max_length=200)

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        input_text = f"translate from {source_lang} to {target_lang}: {text}"
        input_ids = self.tokenizer(input_text, return_tensors="pt")
        outputs = self.model.generate(**input_ids)
        translated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return translated_text

    def back_translate(self, text: str) -> str:
        french_text = self.translate(text, "English", "French")
        back_translated_text = self.translate(french_text, "French", "English")
        return back_translated_text

