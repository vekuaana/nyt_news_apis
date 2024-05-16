#!/usr/bin/env python

from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='nyt_news',
    version='0.0.1',
    author='saa',
    description='Project DE with NYT API',
    package_dir={'nyt_news': 'nyt_news'},
    packages=['nyt_news'],
    install_requires=required,
)

