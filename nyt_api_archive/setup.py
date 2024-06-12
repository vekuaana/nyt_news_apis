from setuptools import setup, find_packages

setup(
    name='nyt_api_archive',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'requests',
        'pymongo'
    ],
    entry_points={
        'console_scripts': [
            'nyt_api_archive=main:main'
        ]
    }
)
