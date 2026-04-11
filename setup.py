"""
setup.py
Setup script for packaging the Paper Trading Bot.
This is for educational paper trading simulations only.
Do not use for real financial transactions.
"""
from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = [
        line.strip() for line in f
        if line.strip() and not line.startswith("#")
    ]

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="paper-trading-bot",
    version="1.0.9",
    author="Mohamed Dodda",
    description="AI-Powered Crypto Paper Trading Bot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mohameddodda/Paper_trading_bot",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "paperbot=bots.cli_bot:main",
        ]
    }
)

