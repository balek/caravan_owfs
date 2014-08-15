#!/usr/bin/env python

from setuptools import setup

setup(name='caravan_owfs',
    version='0.0.1',
    description='OWFS module for Caravan',
    author='Alexey Balekhov',
    author_email='a@balek.ru',
    py_modules = ['caravan_owfs'],
    entry_points = {
        'autobahn.twisted.wamplet': [ 'owfs = caravan_owfs:AppSession' ]
    })