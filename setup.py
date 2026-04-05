"""
setup.py
Setup script for packaging the Paper Trading Bot.
This is for educational paper trading simulations only.
Do not use for real financial transactions.
"""

from setuptools import setup, find_packages

# Read the README for long description (assumes README.md exists)
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="paper-trading-bot",
    version="1.7.0",
    author="Mohamed Dodda",
    author_email="email here",
    description="A Python-based paper trading simulation bot for educational purposes. Fetches stock/crypto data, applies strategies, and backtests trades.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mohameddodda/Paper_trading_bot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "License :: OSI Approved :: Apache License 2.0",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.8",
    install_requires=[
        "yfinance>=0.2.28",
        "requests>=2.31.0",
        "pandas>=2.2.0",
        "numpy>=1.26.4",
        "matplotlib>=3.8.0",
        "plotly>=5.15.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": ["pytest>=7.4.3", "black>=23.9.1", "isort>=5.12.0", "flake8>=6.1.0", "mypy>=1.3.0", "pre-commit>=3.4.0"],
        "jupyter": ["jupyterlab>=4.0.0", "notebook>=6.5.0", "ipykernel>=6.25.0"],
        "ai": ["tensorflow>=2.15.0", "stable-baselines3>=2.2.0", "gymnasium>=0.29.0"],
        "gui": ["customtkinter>=5.2.0", "Pillow>=10.0.0"],
    },
    entry_points={
        "console_scripts": [
            "paper-bot= bots.cli_bot:main",
            "paper-beast= bots.beast_bot:main",
"paper-gui= bots.gui_bot:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
