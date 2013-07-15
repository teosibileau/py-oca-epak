# -*- coding: utf-8 -*-
import os
from distutils.core import setup
from setuptools import find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='ocaepak',
    version='0.1',
    author=u'Teofilo Sibileau',
    author_email='teo.sibileau@gmail.com',
    url='https://github.com/drkloc/py-oca-epak',
    license='BSD licence, see LICENCE.txt',
    description='A python epak wrapper for oca-epak',
    packages=['ocaepak'],
    include_package_data=True,
    zip_safe=False,
    install_requires=required,
)
