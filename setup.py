#!/usr/bin/env python
# # coding: utf-8
from setuptools import find_packages, setup

setup(
    name='coredata_python_client',
    version='0.1',
    description='A client to the Coredata API',
    author='Kristján Oddsson',
    author_email='koddsson@gmail.com',
    url='https://github.com/koddsson/coredata-python-client',
    install_requires=[
        'argparse==1.2.1',
        'docopt==0.6.1',
        'enum34==1.0',
        'requests==2.3.0',
        'wsgiref==0.1.2'
    ],
    packages=find_packages(),
)
