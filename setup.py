from setuptools import setup, find_packages

setup(
    name="paper-trading-bot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "yfinance==0.2.28",
        "python-dotenv==1.0.0",
        "requests==2.31.0",
    ],
    entry_points={
        "console_scripts": [
            "paper-bot=src.bot:main",
        ],
    },
)