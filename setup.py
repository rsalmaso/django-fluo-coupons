import io
from setuptools import setup, find_packages

import coupons


with io.open('README.md', "rt", encoding='utf-8') as fp:
    long_description = fp.read()


setup(
    name="django-fluo-coupons",
    version=coupons.__version__,
    description="A reuseable Django application for coupon gereration and handling.",
    long_description=long_description,
    license="BSD",
    author=coupons.__author__,
    author_email=coupons.__email__,
    url="https://bitbucket.org/rsalmaso/django-fluo-coupons",
    include_package_data=True,
    packages=find_packages(),
    install_require=["django-fluo"],
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
