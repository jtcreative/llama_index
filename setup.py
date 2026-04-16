#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    packages=find_packages(include=["backend", "backend.*"]),
    package_data={
        "backend": ["**/*.py"],
    },
    zip_safe=False,
)
