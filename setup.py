from setuptools import setup, find_packages

setup(
    name="FisioAccess",
    version="1.0.0",
    author="Vanessa",
    author_email="vanessauribe858@gmail.com",
    description="Software para la toma de electrocardiograma",
    packages=find_packages(),
    install_requires=[
        "PySide6>=6.0.0",
        "pytest>=7.0.0",
    ],
    entry_points={
        "console_scripts": [
            "FisioAccess=src.main:main",
        ],
    },
)
