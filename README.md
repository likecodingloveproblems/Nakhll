
# Nakhll

[NAKHLL_DESCRIPTION]

## App Installation and setup

### Linux

1. `sudo apt install git postgresql virtualenv lzma lzma-dev python3 python3-dev libmysqlclient-dev`
2. `git clone https://github.com/nakhll-company/nakhll_backend && cd nakhll_backend`
3. `virtualenv .venv`
4. `source .venv/bin/activate`
5. `pip install -r requirements.txt`

### Windows

1. Install python3 from [python website](https://www.python.org/downloads/windows/)
2. Install Git, postgres
3. `git clone https://github.com/nakhll-company/nakhll_backend && cd nakhll_backend`
4. `C:/Program Files/python3/bin/python -m venv .venv`
5. `.venv/bin/activate.bat`
6. `pip install -r requirements.txt`

## Database setup

1. `sudo -su postgres`
2. `psql`
3. `CREATE ROLE nakhll WITH ENCRYPTED PASSWORD '12345';`
4. `CREATE DATABASE nakhlldb;`
5. `GRANT ALL PRIVILEGES ON DATABASE nakhlldb TO nakhll;`
6. `ALTER ROLE "nakhll" WITH LOGIN;`

## .env setup

Rename `sample.env` to `.env`, fill all data that is available

## Start app

1. `python3 manage.py migrate`
2. `python3 manage.py runserver`



## Config linter for project

We use `autopep8` and `pylint` for formatting and linting our project. Code is
much more cleaner and readable in result. Here is how you can config formatter
and linter:

### VSCode

1. Install `pep8`, `autopep8`, `pylint`, `pylint-django` using `pip`. You
   probably installed them while installing all project dependencies using
   `pip install -r requirements.txt`
2. Add this lines to `settings.json` file in vscode (<kbd>Ctrl</kbd> + <kbd>,</kbd>
   or File > Preferences > Settings):

```
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.linting.pycodestyleEnabled": true,
    "python.formatting.provider": "autopep8",
    "python.linting.pylintArgs": [
        "--load-plugins=pylint_django"
    ],
    "python.formatting.autopep8Args": [
        "--max-line-length",
        "80",
        "--aggressive",
        "--experimental"
    ],
    "editor.formatOnSave": true,
    "editor.formatOnSaveMode": "modifications",
}
```

### PyCharm

[COMPLETE_THIS_SECTION]


