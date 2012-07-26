#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'guotie'
from setuptools import setup

setup(
    name='flaskbbs',
    version='0.5',
    url='<enter URL here>',
    license='MIT',
    author='guotie',
    author_email='your-email-here@example.com',
    description='A simple bbs base on flask framework.',
    long_description=__doc__,
    packages=['flaskbbs'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
        'Flask-Cache',
        'Flask-SQLAlchemy',
        'Flask-WTF',
        'Flask-Testing',
        'Flask-Script',
        'Flask-Login',
        'Flask-Babel',
        'Flask-Themes',
        'sqlalchemy',
        'markdown2',
        'blinker',
        'nose',
        ],
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        ]
)