# Contributing to Reforger Whitelist

Thank you for considering contributing to Reforger Whitelist! Your contributions help make this project better for everyone. Below are some guidelines to help you get started.

## Table of Contents
- [Contributing to Reforger Whitelist](#contributing-to-reforger-whitelist)
  - [Table of Contents](#table-of-contents)
  - [Code of Conduct](#code-of-conduct)
  - [How Can I Contribute?](#how-can-i-contribute)
    - [Reporting Bugs](#reporting-bugs)
    - [Suggesting Enhancements](#suggesting-enhancements)
    - [Submitting Pull Requests](#submitting-pull-requests)
  - [Development Setup](#development-setup)
  - [Style Guides](#style-guides)
    - [Python Style Guide](#python-style-guide)
    - [Commit Messages](#commit-messages)
  - [License](#license)

## Code of Conduct
This project adheres to the Contributor Covenant [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [email@example.com](mailto:email@example.com).

## How Can I Contribute?

### Reporting Bugs
If you find a bug, please report it by opening an issue on the [GitHub Issues](https://github.com/BreathXV/ReforgerWhitelistPy/issues) page. Include as much detail as possible to help us understand and reproduce the issue.

### Suggesting Enhancements
If you have an idea for an enhancement, please open an issue on the [GitHub Issues](https://github.com/BreathXV/ReforgerWhitelistPy/issues) page. Describe your idea in detail and explain why it would be beneficial to the project.

### Submitting Pull Requests
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeature`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add some feature'`).
5. Push to the branch (`git push origin feature/YourFeature`).
6. Open a pull request.

Please ensure your pull request adheres to the following guidelines:
- Include a clear description of what your pull request does.
- Reference any related issues in the pull request description.
- Ensure your code follows the project's style guides.
- Write tests for your code if applicable.

## Development Setup
To set up your development environment, follow these steps:

1. Clone the repository:
    ```sh
    git clone https://github.com/BreathXV/ReforgerWhitelistPy.git
    cd ReforgerWhitelistPy
    ```

2. Create a virtual environment:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Run the tests to ensure everything is set up correctly:
    ```sh
    pytest
    ```

## Style Guides

### Python Style Guide
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code.
- Use type hints where appropriate.
- Write docstrings for all public modules, functions, classes, and methods.

### Commit Messages
- Use the present tense ("Add feature" not "Added feature").
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...").
- Limit the first line to 72 characters or less.
- Reference issues and pull requests liberally.

## License
By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).

Thank you for contributing!