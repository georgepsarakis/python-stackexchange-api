import ast
import re
from setuptools import setup, find_packages

_version_re = re.compile(r'__version__\s+=\s+(.*)')


with open('stackexchange/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))


setup(
    name="stackexchange",
    version=version,
    description="StackExchange API Python Client",
    packages=find_packages(),
    install_requires=[
        "requests==2.10.0"
    ],
    test_suite="tests",
    tests_require=[
        "mock==2.0.0",
        "flake8==3.0.4"
    ]
)
