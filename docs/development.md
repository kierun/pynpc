# Development

## Virtual Environment

Please use a virtual environment when developing and do run `tox` from time to time to
make sure that your changes are compatible with all the Python version we have to support.

## UV

This needs better documentation…

```bash
uv sync --upgrade
uv lock --upgrade
```

## pre-commit

Please use [pre-commit](https://pre-commit.com/) which can be setup via:

```bash
pre-commit install
pre-commit install --hook-type commit-msg
```

## Conventional commits

We use [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/).

You can use [commitizen](https://github.com/commitizen-tools/commitizen) to create correct
conventional commits if it helps you. If not, the `pre-commit` hooks should validate if
your commit is correct or not.

Note that a GHA should run to make sure that the RP title is a valide
[conventional commits](https://www.conventionalcommits.org/en/v1.0.0/).

## Testing

### PyTest

There are two sets of test one can run `task tests-fast` and `task tests`. The former will
not run the functional tests that actually do use the network and take time to run. The
latter will run all the tests.

### Coverage

We have 100% test coverage — with a few cheats using `pragma: no sover` for code should be
excluded.

The GHA should create a nice coverage report.

## Release

There is a GitHub Action that will create a
[semantic release](https://python-semantic-release.readthedocs.io/en/latest/) for Setupr.

This is why [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) are
essential, especially in PR titles.

## Linters

We use [ruff](https://github.com/charliermarsh/ruff), because it is both good and fast.
