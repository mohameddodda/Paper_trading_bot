from setuptools import setup, find_packages

setup(
    name="paper-trading-bot",
    version="3.0.0",
    packages=find_packages(),
    install_requires=[
        'numpy>=1.24',
        'pandas',
        'yfinance',
        'requests',
        'python-dotenv',
        'streamlit',
        'quantstats',
        'ta',
        'websocket-client',
        'pytest',
        'rich',
    ],
    python_requires='>=3.9',
    description="Educational Paper Trading Bot with AI signals and backtesting",
    author="Mohamed Dodda",
    license="Apache-2.0",
    entry_points={
        'console_scripts': [
            'paper-bot=bot:main',
        ],
    },
)

