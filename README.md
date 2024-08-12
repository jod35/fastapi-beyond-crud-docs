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

- Python 3.x

## Project Setup
To set up the project, follow these steps:

1. **Clone the repository:**
    ```bash
    git clone https://github.com/jod35/fastapi-beyond-crud-docs.git
    ```

2. **Navigate into the project directory:**
    ```bash
    cd fastapi-beyond-crud-docs
    ```

3. **Create a virtual environment:**
   - On macOS/Linux:
     ```bash
     python3 -m venv venv
     ```
   - On Windows:
     ```bash
     python -m venv venv
     ```

4. **Activate the virtual environment:**
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

5. **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

6. **Run the application:**
    ```bash
    mkdocs serve
    ```

Your application should now be up and running within the virtual environment.
