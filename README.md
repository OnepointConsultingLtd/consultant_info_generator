# Consultant Information Generator

The purpose of this project is to extract information from webpages and generate the data needed for consultant profile creation.

# Installation

## Setup

We suggest to use [uv](https://github.com/astral-sh/uv) to manage the virtual environment and then install poetry.

```powershell
uv venv
./.venv/Scripts/activate
uv sync
```

```bash
uv venv
source .venv/bin/activate
uv sync
```

## Database

You will need a Postgres database which you can setup using the script: [db_creation.sql](./sql/db_creation.sql)

Then you can install all of the tables by running this script  [db_setup.sql](./sql/db_setup.sql)

## Environment

You will need the environment variables listed in [.env_local](.env_local) in order to run the main customer import.

# Running import

In order to run the main import you will need to collect some LinkedIn public profiles like the one you can find in [profiles.txt](./data/profiles.txt).

The you can turn on the Python environment using venv for example and run this command pointing to a file with LinkedIn profiles:

```python
python consultant_info_generator/cli/main.py import-consultants-with-categories-file -f data/profiles.txt --remove-existing
```

