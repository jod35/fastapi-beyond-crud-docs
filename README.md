Here's the updated markdown with instructions for setting up a virtual environment:

# FastAPI Beyond the CRUD Stuff

Welcome to the documentation for the FastAPI Beyond CRUD course.

## Table of Contents
- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [Project Setup](#project-setup)
- [Running the Application](#running-the-application)

## Introduction
This repository contains the source code for the course website.

## Prerequisites

Before starting, make sure you have the following installed:

- Python 3.10+
- Git
- pip

### Verify Installation

```bash
python --version
git --version
pip --version
```

## Project Setup
To set up the project, follow these steps:

1. Fork the Repository

Click the **Fork** button at the top-right corner of the repository page on GitHub.

---

2. **Clone the repository:**
    ```bash
    git clone https://github.com/YOUR_USERNAME/fastapi-beyond-crud-docs.git
    ```

3. **Navigate into the project directory:**
    ```bash
    cd fastapi-beyond-crud-docs
    ```

4. **Create a virtual environment:**
   - On macOS/Linux:
     ```bash
     python3 -m venv venv
     ```
   - On Windows:
     ```bash
     python -m venv venv
     ```

5. **Activate the virtual environment:**
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
        > After activation, you should see `(venv)` in your terminal.

6. **Install the required dependencies:**
    ```bash
    python -m pip install -r requirements.txt
    ```

7. **Run the application:**
    ```bash
    mkdocs serve
    ```
    ### Open in Browser

    Once the server starts successfully, open your browser and visit:

    ```text
    http://127.0.0.1:8000/
    ```

---


Your application should now be up and running within the virtual environment.

## Project Structure

```text
fastapi-beyond-crud-docs/
│
├── docs/
├── mkdocs.yml
├── requirements.txt
└── README.md
```

---
## Contributing

Contributions are welcome.

Follow these steps:

1. Fork the repository
2. Create a new branch

```bash
git checkout -b feature-name
```

3. Make your changes
4. Commit your changes

```bash
git commit -m "Added new feature"
```

5. Push your changes

```bash
git push origin feature-name
```

6. Create a Pull Request
