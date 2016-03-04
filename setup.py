#!/usr/bin/env python
from setuptools import setup, find_packages

__version__ = "0.1"


setup(
    name="megserver",
    author="Gregory Rehm",
    version=__version__,
    description="Server component for MEG",
    packages=find_packages(exclude=["*.tests"]),
    package_data={"*": ["*.html"]},
    install_requires=[
        "configmaster>=2.3.6",
        "Flask>=0.10.1",
        "Flask-SQLAlchemy>=2.0",
        "gunicorn",
        "pgpdump>=1.5",
        "psycopg2>=2.6.1",
        "PyYAML>=3.11",
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "development=meg.development:main",
        ]
    }
)
