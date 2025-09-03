# Skillormeter
Test ideas about measure skills

## Setup

This project uses `pyenv` and `poetry` for dependency management and virtual environments.

### Dependencies Installation

#### Install `pyenv`:

```sh
brew update
brew install pyenv
```

#### Install `poetry`:

```sh
curl -sSL https://install.python-poetry.org | python3 -
```

After installing `pyenv` and `poetry`, set up the Python version and install the project dependencies:

```sh
pyenv install 3.11
pyenv local 3.11
poetry env use 3.11
poetry install
```

export environment variables:

```
aws sso login --profile smoke
export AWS_PROFILE=smoke
```

If you are using VSCode, activate python interpretator by pressing cmd+shif+p

![alt text](<Screenshot 2025-09-04 at 10.17.02 am.png>)

### Run the script
```
poetry run python -m  src.skillormeter
```


