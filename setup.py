from setuptools import setup, find_packages

setup(
    name="pdf_works",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "PyMuPDF",
        "click"
    ],
)
