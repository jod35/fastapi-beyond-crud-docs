# Getting Started

In this chapter, we install FastAPI, starting with a minimal setup.

### Prerequisites

Before we begin, ensure you have the following installed:

- Python 3.12 or higher
- A text Editor like [VS Code](https://code.visualstudio.com/), [PyCharm](https://www.jetbrains.com/pycharm/), [Zed](https://zed.dev/), or any other text editor of your choice

- A unix-like environment such as Linux, macOS, or Windows with [WSL](https://learn.microsoft.com/en-us/windows/wsl/install)
- [Git](https://git-scm.com/) 
- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/install/)


I will be using [Vs Code](https://code.visualstudio.com/) as my text editor of choice with the [Microsoft Python Extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python). My Operating system of choice will be [Arch Linux](https://archlinux.org/) but any unix-like environment will work just fine. I am also using [Fish](https://fishshell.com/) as my shell of choice. It comes with a lot of features out of the box that make it a great choice for developers. My favorite feature is the tab completion of commands and arguments.


### Installing UV

Throughout this course, we will use [uv](https://docs.astral.sh/uv/) as our package and project manager. Written in Rust, uv is an exceptionally fast and modern alternative to traditional tools like [pip](https://pip.pypa.io/en/stable/), [pipenv](https://pipenv.pypa.io/en/stable/), and [poetry](https://python-poetry.org/docs/). 

Beyond package installation, uv handles:

- **Python Version Management**: Easily switch between different Python versions.
- **Dependency Resolution**: Fast and reliable resolution for complex projects.
- **Builds & Publishing**: Tools for building and distributing your packages.
- **Script Execution**: Run scripts in isolated environments with ease.

