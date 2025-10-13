# Product Services 🛍️ NYU DevOps Project

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

The Products Service is a RESTful microservice that manages product data, providing CRUD (Create, Read, Update, Delete) operations for an online store. It is built with Flask and follows the structure and standards used in the NYU DevOps course.

## Overview

This service provides an API to interact with a catalog of products.
Developers and applications can use the /products endpoint to retrieve, create, update, or delete product records.

The project follows a standard DevOps-ready structure with separate folders for the service logic and test suites.

```

## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
pyproject.toml      - Poetry list of Python libraries required by your code

service/                   - service python package
├── __init__.py            - package initializer
├── config.py              - configuration parameters
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── cli_commands.py    - Flask command to recreate all tables
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/                     - test cases package
├── __init__.py            - package initializer
├── factories.py           - Factory for testing with fake objects
├── test_cli_commands.py   - test suite for the CLI
├── test_models.py         - test suite for business models
└── test_routes.py         - test suite for service routes
```

## Installation

### Prerequisites
- **Python 3.10+**
- **[Poetry](https://python-poetry.org/)** (for dependency management)
- **Git**

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/<your-org>/<your-repo>.git
   cd <your-repo>
2. **Set up the enviorment**
    ```bash 
    cp dot-env-example .env
3. **Install dependencies using Poetry**
    ```bash
    poetry install
4. **Activate the virtual environment**
    ```bash
    poetry shell
5. **Initialize the database (first-time setup)**
    ```bash
    flask db-create
6. **Run the service**
   ```bash
   flask run
By default, the service will be available at http://localhost:8080
7. **Test the service**
    ```bash
    curl http://localhost:8080/products

### Testing
1. **Run all tests**
   ```bash
   pytest

2. **Run with coverage**
   ```bash
   pytest --cov=service
   

## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
