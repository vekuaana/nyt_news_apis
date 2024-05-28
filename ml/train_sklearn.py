# coding:utf-8

import pandas as pd

from sklearn.metrics import classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.svm import SVC, LinearSVC

df = pd.read_csv('..\data\merge_SEN.csv', sep=',', encoding='utf-8')
df = df[df.majority_label != 'UNK']

X = df['headline']
y = df['majority_label']

X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.2, random_state=15)
X_train, X_dev, y_train, y_dev = train_test_split(X_temp, y_temp, test_size=0.2, random_state=15)

le = LabelEncoder()
y_train = le.fit_transform(y_train)
y_dev = le.transform(y_dev)
y_test = le.transform(y_test)
mapping = dict(zip(le.classes_, le.transform(le.classes_)))
labels = le.classes_


pipe = Pipeline([
    ('vect', TfidfVectorizer()),
    ('clf', SGDClassifier(random_state=42,
                          max_iter=5)),
])

pipe2 = Pipeline([
    ('vect', TfidfVectorizer()),
    ('clf', LinearSVC(class_weight='balanced', random_state=42)),
])

print("---- SGD ----")
pipe.fit(X_train, y_train)
y_pred = pipe.predict(X_dev)
print(classification_report(y_dev, y_pred, target_names=le.classes_))
print(f1_score(y_dev, y_pred, average = 'macro'))

print("---- LinearSVC ----")
pipe2.fit(X_train, y_train)
y_pred = pipe2.predict(X_dev)
print(classification_report(y_dev, y_pred, target_names=le.classes_))
print(f1_score(y_dev, y_pred, average = 'macro'))