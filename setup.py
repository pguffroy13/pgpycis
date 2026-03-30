#!/usr/bin/env python3
"""Setup configuration for pgpycis - PostgreSQL CIS Compliance Assessment Tool"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pgpycis",
    version="2.0",
    author="Gilles Darold",
    email="gilles@darold.net",
    description="PostgreSQL Database Security Assessment Tool (Python Version)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hexacluster/pgpycis",
    license="GPL-3.0",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "pgpycis=pgpycis.cli:main",
        ]
    },
    install_requires=[
        "psycopg2-binary>=2.9.0",
        "jinja2>=3.0.0",
        "click>=8.0.0",
        "pyyaml>=6.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Systems Administration",
        "Topic :: Database",
    ],
)
