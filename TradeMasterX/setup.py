from setuptools import setup, find_packages

setup(
    name='TradeMasterX',
    version='0.1.0',
    description='A modular, extensible trading system',
    author='Your Name',
    packages=find_packages(),
    install_requires=[
        'numpy==1.26.4',
        'pandas==2.2.2',
        'pandas-ta==0.3.14b0',
        'yfinance==0.2.38',
        'scikit-learn==1.4.2',
        'matplotlib==3.8.4',
        'plotly==5.21.0',
        'requests==2.31.0',
        'ccxt==4.2.99',
        'pytest==8.2.1',
        'aiohttp==3.9.5',
        'aiohttp-cors==0.7.0',
        'pyyaml==6.0.1',
        'python-dotenv==1.0.1',
    ],
    python_requires='>=3.10',
    include_package_data=True,
) 