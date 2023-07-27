# Contributing to LifeOmic PHC SDK for Python

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

## How can I contribute?

### Improve issues

Some issues are created with missing information, not reproducible, or plain invalid. Help make them easier to resolve. Handling issues takes a lot of time that we could rather spend on fixing bugs and adding features.

### Give feedback on issues

We're always looking for more opinions on discussions in the issue tracker. It's a good opportunity to influence the future direction of the LifeOmic PHC SDK for Python.

## Submitting an issue

- Search the issue tracker before opening an issue.
- Ensure you're using the latest version of the LifeOmic PHC SDK for Python.
- Use a clear and descriptive title.
- Include as much information as possible: Steps to reproduce the issue, error message, Python version, operating system, etc.

## Development

### Prerequisite

- `poetry` - follow the [installation guide](https://python-poetry.org/docs/#installation)

### Install dependencies

```
poetry install
```

Then installs pre-commit hooks that will format and lint new changes.

```bash
poetry run pre-commit
```

### Running tests

```bash
poetry run pytest
```

####Linting

```bash
poetry run poe lint
```

### Generate code

Some clients in this SDK are auto-generated. They can be re-generated at any
time to pull in the latest changes by running `poetry run poe gen`.

### Build

```bash
poetry build
```

## Release Process

[Releases](https://github.com/lifeomic/phc-sdk-py/releases) are generally created
with each merged PR. To release a new version, update the package version in
`pyproject.toml`, and open a PR.

Packages for each release are published to [PyPi](https://pypi.org/project/phc/).
See [CHANGELOG.md](CHANGELOG.md) for release notes.

### Versioning

This project uses [Semantic Versioning](http://semver.org/).

## Submitting a pull request

- Non-trivial changes are often best discussed in an issue first, to prevent you from doing unnecessary work.
- For ambitious tasks, you should try to get your work in front of the community for feedback as soon as possible. Open a pull request as soon as you have done the minimum needed to demonstrate your idea. At this early stage, don't worry about making things perfect, or 100% complete. Add a [WIP] prefix to the title, and describe what you still need to do. This lets reviewers know not to nit-pick small details or point out improvements you already know you need to make.
- New features should be accompanied with tests.
- Don't include unrelated changes.
- Lint and test before submitting the pull request by running `$ poetry run poe lint && poetry run pytest`.
- Use a clear and descriptive title for the pull request and commits.
- Write a convincing description of why we should land your pull request. It's your job to convince us. Answer "why" it's needed and provide use-cases.
- Break up large changes into multiple pull requests. Smaller changes are easier to review and more likely to get merged faster.
- You might be asked to do changes to your pull request. There's never a need to open another pull request. [Just update the existing one.](https://github.com/RichardLitt/knowledge/blob/master/github/amending-a-commit-guide.md)
