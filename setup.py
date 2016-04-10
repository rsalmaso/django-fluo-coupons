import os
from setuptools import setup, find_packages

import coupons


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="django-fluo-coupons",
    version=coupons.__version__,
    description="A reuseable Django application for coupon gereration and handling.",
    long_description=read("README.md"),
    license=read("LICENSE"),
    author="Raffaele Salmaso",
    author_email="raffaele@salmaso.org",
    url="https://bitbucket.org/rsalmaso/django-fluo-coupons",
    include_package_data=True,
    packages=find_packages(),
    classifiers=[
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ]
)
