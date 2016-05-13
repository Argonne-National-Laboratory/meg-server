#!/usr/bin/env python
from setuptools import setup, find_packages

__version__ = "0.5.1"


setup(
    name="megserver",
    author="Gregory Rehm",
    version=__version__,
    description="Server component for MEG",
    packages=find_packages(exclude=["*.tests"]),
    data_files=[('config', ['meg/config.default.yml'])],
    install_requires=[
        "celery==3.1.22",
        "configmaster>=2.3.6",
        "Flask>=0.10.1",
        "Flask-SQLAlchemy>=2.0",
        "gunicorn==19.4.5",
        "pgpdump>=1.5",
        "psycopg2>=2.6.1",
        "python-gcm==0.4",
        "PyYAML>=3.11",
        "requests==2.9.1",
        "sendgrid==2.2.1",
    ],
    entry_points={
        "console_scripts": [
            "development=meg.development:main",
        ]
    }
)
