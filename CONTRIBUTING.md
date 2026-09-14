# Contributing to Django Immediate ForeignKey

## Local development

### Installation

Ensure one of the supported versions of Python is installed.

Create and activate a virtual environment with a tool of your choosing.
For example:

```sh
python -m venv .venv
source .venv/bin/activate
```

Once you are in an active virtual environment,
install Python requirements:

```sh
pip install --group dev --editable .
```
*The `--group` flag requires a minimum pip version of 25.1*

### Testing

To test against all supported databases, we need to:

- Ensure that postgres is installed and available on your system.
- Install the [`just` command runner](https://just.systems/man/en/).

Then run full coverage with:

```sh
just coverage
```

You can also run against sqlite with:

```sh
just test-sqlite
```

And against postgres with:

```sh
just test-postgres
```

If you don't like using `just`, you can also copy the commands from the `justfile`.

### Dependencies

Python dependencies are declared in `pyproject.toml`.

- _package_ dependencies in the `dependencies` array in the `[project]` section.
- _development_ dependencies in the `[dependency-groups]` section.
