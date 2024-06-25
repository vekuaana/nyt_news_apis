import os


def faker():
    with open('..' + os.sep + 'models' + os.sep + 'mytest2.txt') as f:
        text = f.read()
    return text
