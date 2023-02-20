# XKNXCLI - An asynchronous KNX CLI tool

## Development

You will need at least Python 3.9 in order to use XKNX.

Setting up your local environment:

1. Create a Python virtual environment: `python -m venv venv`
2. Activates the virtual environment: `venv\Scripts\activate.bat`
3. Install requirements: `pip install -r requirements/testing.txt`
4. Install pre-commit hook: `pre-commit install`

## Run Tests Local

1. `pre-commit run --all-files`
2. `python -m pytest --cov xknxcli --cov-report term-missing`

## Run CLI Local

1 `python -m xknxcli`
