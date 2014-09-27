#!/usr/bin/env python
# # coding: utf-8
from setuptools import setup

setup(
    name='coredata',
    packages=['coredata'],
    version='0.1.3',
    description='A client to the Coredata API',
    author='Kristján Oddsson',
    author_email='koddsson@gmail.com',
    url='https://github.com/koddsson/coredata-python-client',
    download_url=('https://github.com/koddsson/coredata-python-client'
                  '/tarball/0.1.3'),
    keywords = ['coredata'],
    classifiers = [],
    install_requires=[
        'requests==2.3.0'
    ],
)
