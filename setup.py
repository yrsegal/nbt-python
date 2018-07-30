from setuptools import setup

CLIENT_VERSION = "1.0.0"
PACKAGE_NAME = "nbt"

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

setup(
    name=PACKAGE_NAME,
    version=CLIENT_VERSION,
    description="NBT loader",
    author_email="yrsegal@gmail.com",
    author="Wire Segal",
    license="MIT License"
)
