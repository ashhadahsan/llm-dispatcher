"""Shim setup.py for legacy tooling.

All package metadata, dependencies, and extras are declared in pyproject.toml.
Modern pip uses pyproject.toml directly; this file exists only for tools that
still invoke setup.py.
"""

from setuptools import setup

setup()
