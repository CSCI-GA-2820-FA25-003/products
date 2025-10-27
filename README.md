# Product Services 🛍️ NYU DevOps Project

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)
[![CI Build](https://github.com/CSCI-GA-2820-FA25-003/products/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-FA25-003/products/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-FA25-003/products/graph/badge.svg?token=7MTYI7GT9N)](https://codecov.io/gh/CSCI-GA-2820-FA25-003/products)

The Products Service is a RESTful microservice that manages product data, providing CRUD (Create, Read, Update, Delete) operations for an online store. It is built with Flask and follows the structure and standards used in the NYU DevOps course.

## Overview

This service provides an API to interact with a catalog of products.
Developers and applications can use the /products endpoint to retrieve, create, update, or delete product records.

The project follows a standard DevOps-ready structure with separate folders for the service logic and test suites.

## Contents
The project contains the following:
```
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

k8s/ - Kubernetes deployment manifests
├── deployment.yaml - Product Service Deployment
├── service.yaml - Product Service (LoadBalancer/ClusterIP)
├── configmap.yaml - Configuration and environment variables
└── postgres/ - PostgreSQL database manifests
    ├── deployment.yaml - PostgreSQL Deployment
    ├── service.yaml - PostgreSQL Service
    └── pvc.yaml - Persistent Volume Claim for data storage
```


## Installation

### Prerequisites
- **Python 3.10+**
- **[Poetry](https://python-poetry.org/)** (for dependency management)
- **Git**
- **Docker** (for containerization)
- **kubectl** and **Minikube** or a Kubernetes cluster (for deployment)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/CSCI-GA-2820-FA25-003/products.git
   cd products
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

## Kubernetes Deployment
---

1. **Build and Push the Docker Image**
   ```bash
    docker build -t <your-dockerhub-username>/products-service:latest .
    docker push <your-dockerhub-username>/products-service:latest
   
2. **Deploy the PostgreSQL Database**
    ```bash
    kubectl apply -f k8s/postgres/
    
3. **Check the status**
    ```bash
    kubectl get pods
    kubectl get pvc
    kubectl get services
    
4. **Deploy the Product Service**
    ```bash
    kubectl apply -f k8s/configmap.yaml
    kubectl apply -f k8s/deployment.yaml
    kubectl apply -f k8s/service.yaml
    
4.1 **Verify everything is running**
    ```bash
    
    kubectl get pods
    kubectl get services
    
4.2 **Optional, however if using Minikube, you can access the service**
    ```bash
    
    minikube service products-service
    
5. **Configure Environment Variables**
    ```bash
    FLASK_ENV: production
    PORT: "8080"
    DATABASE_URI: postgresql://postgres:postgres@postgres:5432/products
    
6. **Scaling and Updating the Deployment**
    ```bash
    kubectl scale deployment products-deployment --replicas=3
    kubectl set image deployment/products-deployment products=<your-dockerhub-username>/products-service:latest
    
7. **Cleanup (Optional)**
    ```bash
    kubectl delete -f k8s/service.yaml
    kubectl delete -f k8s/deployment.yaml
    kubectl delete -f k8s/configmap.yaml
    kubectl delete -f k8s/postgres/

## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
