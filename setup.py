# -*- coding: utf-8 -*-
"""
Created on Fri Jul 11 16:13:08 2025

@author: ferna
"""

from setuptools import setup, find_packages

setup(
    name='hub_o',
    version='0.1',
    description='Client API pour les services Hub’Eau (biodiversité, pollution, eau potable...)',
    author='Fernand Fort',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'requests'
    ],
    python_requires='>=3.7'
)
