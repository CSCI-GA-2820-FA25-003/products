# Product Services 🛍️

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)
[![CI Build](https://github.com/CSCI-GA-2820-FA25-003/products/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-FA25-003/products/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-FA25-003/products/graph/badge.svg?token=7MTYI7GT9N)](https://codecov.io/gh/CSCI-GA-2820-FA25-003/products)

## Overview

The **Products Service** is a production-ready RESTful microservice for managing product catalog data in an e-commerce application. Built with Flask-RESTX and following DevOps best practices, it provides comprehensive CRUD operations with advanced features like pagination, querying, and product lifecycle management.

This service is part of the NYU DevOps course (CSCI-GA.2820-003) and demonstrates the complete software development lifecycle from planning through deployment, including CI/CD pipelines, automated testing, and Kubernetes orchestration.

### Key Features

- **Full CRUD Operations**: Create, Read, Update, and Delete products
- **Advanced Querying**: Filter products by name, category, and availability
- **Pagination Support**: Efficient handling of large product catalogs
- **Product Actions**: Favorite/unfavorite and discontinue products
- **Swagger/OpenAPI Documentation**: Interactive API documentation at `/apidocs`
- **RESTful Design**: Follows REST API best practices with proper HTTP methods and status codes
- **High Test Coverage**: 95%+ code coverage with comprehensive unit and BDD tests
- **Production Ready**: Deployed on Kubernetes/OpenShift with automated CI/CD pipelines

---

## 📋 Table of Contents

- [Product Model](#product-model)
- [API Endpoints](#api-endpoints)
- [Getting Started](#getting-started)
- [Running the Service](#running-the-service)
- [Testing](#testing)
- [Kubernetes Deployment](#kubernetes-deployment)
- [CI/CD Pipeline](#cicd-pipeline)
- [Development Workflow](#development-workflow)
- [Team](#team)

---

## Product Model

Products have the following attributes:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | Integer | Auto | Unique identifier |
| `name` | String(63) | Yes | Product name |
| `description` | String(1023) | No | Product description |
| `price` | Numeric(14,2) | Yes | Product price (stored as string in JSON) |
| `image_url` | String(1023) | No | URL to product image |
| `category` | String(63) | No | Product category |
| `availability` | Boolean | No | Stock availability (default: true) |
| `favorited` | Boolean | No | User favorite status (default: false) |
| `discontinued` | Boolean | No | Product discontinuation status (default: false) |
| `created_date` | DateTime | Auto | Product creation timestamp |
| `updated_date` | DateTime | Auto | Last update timestamp |

**Note**: Discontinued products are filtered out from list and query operations.

---

## API Endpoints

All API endpoints are prefixed with `/api` and documented at `/apidocs`.

### Product Collection

#### `GET /api/products`
List all products with optional filtering and pagination.

**Query Parameters**:
- `name` - Filter by product name (case-insensitive partial match)
- `category` - Filter by category (case-insensitive partial match)
- `availability` - Filter by availability (`true`/`false`)
- `page` - Page number for pagination (starts at 1)
- `limit` - Items per page (default: all)

**Example**:
```bash
# Get all products
curl -X GET http://localhost:8080/api/products

# Filter by category
curl -X GET "http://localhost:8080/api/products?category=electronics"

# Pagination
curl -X GET "http://localhost:8080/api/products?page=1&limit=10"
```

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "name": "Wireless Mouse",
    "description": "Ergonomic wireless mouse",
    "price": "29.99",
    "category": "Electronics",
    "availability": true,
    "favorited": false,
    "discontinued": false,
    "image_url": "https://example.com/mouse.jpg",
    "created_date": "2024-10-15T10:30:00Z",
    "updated_date": "2024-10-15T10:30:00Z"
  }
]
```

#### `POST /api/products`
Create a new product.

**Request Body**:
```json
{
  "name": "Wireless Mouse",
  "description": "Ergonomic wireless mouse",
  "price": "29.99",
  "category": "Electronics",
  "image_url": "https://example.com/mouse.jpg",
  "availability": true
}
```

**Response**: `201 Created`
- Returns created product with `id` and timestamps
- Includes `Location` header with product URL

### Individual Product

#### `GET /api/products/{id}`
Retrieve a specific product by ID.

**Response**: `200 OK` or `404 Not Found`

#### `PUT /api/products/{id}`
Update an existing product.

**Request Body**: Same as POST (all fields except `id`)

**Response**: `200 OK` or `404 Not Found`

#### `DELETE /api/products/{id}`
Delete a product.

**Response**: `204 No Content`

### Product Actions

#### `PUT /api/products/{id}/favorite`
Mark a product as favorite.

**Response**: `200 OK`
```json
{
  "id": 1,
  "favorited": true
}
```

#### `PUT /api/products/{id}/unfavorite`
Remove product from favorites.

**Response**: `200 OK`
```json
{
  "id": 1,
  "favorited": false
}
```

#### `POST /api/products/{id}/discontinue`
Discontinue a product (requires confirmation).

**Query Parameters** or **Request Body**:
- `confirm=true` (required)

**Example**:
```bash
# Using query parameter
curl -X POST "http://localhost:8080/api/products/1/discontinue?confirm=true"

# Using request body
curl -X POST http://localhost:8080/api/products/1/discontinue \
  -H "Content-Type: application/json" \
  -d '{"confirm": true}'
```

**Response**: `200 OK` or `400 Bad Request` (if not confirmed)

### Health Check

#### `GET /api/health`
Kubernetes liveness/readiness probe endpoint.

**Response**: `200 OK`
```json
{
  "status": "OK"
}
```

---

## Getting Started

### Prerequisites

- **Python 3.11+**
- **pipenv** (dependency management)
- **Docker** (for containerization)
- **kubectl** and **K3D** (for local Kubernetes deployment)
- **Git**

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/CSCI-GA-2820-FA25-003/products.git
   cd products
   ```

2. **Open in VSCODE**
   ```bash
   code .
   ```

3. **Initialize the database** (first-time setup)
   ```bash
   flask db-create
   ```

---

## Running the Service

### Local Development

```bash
# Using honcho (recommended)
make run

# Or directly with Flask
flask run
```

The service will be available at `http://localhost:8080`

- **Web UI**: `http://localhost:8080/`
- **API Documentation**: `http://localhost:8080/apidocs`
- **Health Check**: `http://localhost:8080/api/health`

### Using Make Commands

```bash
make help          # Display all available commands
make install       # Install dependencies
make lint          # Run code quality checks
make test          # Run tests with coverage
make run           # Start the service
```

---

## Testing

### Unit Tests

The project uses pytest with comprehensive test coverage (95%+ required).

```bash
# Run all tests with coverage
make test

# Run tests with detailed output
pytest --pspec --cov=service --cov-fail-under=95
```

### Behavior-Driven Development (BDD) Tests

Integration tests using Behave and Selenium WebDriver.

```bash
# Run BDD tests
behave
```

**BDD Scenarios**:
- Create a product
- Read product details
- Update a product
- Delete a product
- List all products
- Query products by name/category/availability
- Favorite/unfavorite products
- Discontinue products

### Code Quality

```bash
# Run linting
make lint

# Individual linters
flake8 service tests
pylint service tests --max-line-length=127
```

---

## Kubernetes Deployment

### Local Deployment (K3D)

1. **Create a local Kubernetes cluster**
   ```bash
   make cluster
   ```
   This creates a K3D cluster with 2 worker nodes, a registry, and load balancer.

2. **Build the Docker image**
   ```bash
   make build
   ```

3. **Push image to local registry**
   ```bash
   make push
   ```

4. **Deploy the application**
   ```bash
   make deploy
   ```

5. **Verify deployment**
   ```bash
   kubectl get pods
   kubectl get services
   kubectl get deployments
   ```

6. **Access the service**
   ```bash
   # Service is available at http://localhost:8080
   curl http://localhost:8080/api/health
   ```

### Production Deployment (OpenShift)
1. **Log in your account**
   ```bash
   oc login *****
   ```

2. **Apply PostgreSQL resources**
   ```bash
   oc apply -f k8s/postgres/
   ```

3. **Apply Tekton tasks, pipeline, routes, triggers and workspace(please update default ROUTE_URL)**
   ```bash
   oc apply -f .tekton/
   ```

The service is already deployed on Red Hat OpenShift.

**Deployed Service**: `https://products-luoashley-dev.apps.rm3.7wse.p1.openshiftapps.com/`

### Kubernetes Manifests

Located in the `k8s/` directory:

```
k8s/
├── deployment.yaml      # Products service deployment
├── service.yaml         # Service definition
├── configmap.yaml       # Configuration
├── ingress.yaml         # Ingress rules
└── postgres/            # PostgreSQL manifests
    ├── deployment.yaml  # Database deployment
    ├── service.yaml     # Database service
    └── pvc.yaml         # Persistent volume claim
```

---

## CI/CD Pipeline

### Continuous Integration (GitHub Actions)

Every push and pull request triggers automated checks:

**Workflow** (`.github/workflows/ci.yml`):
1. **Checkout code**
2. **Install dependencies** (pipenv)
3. **Lint code** (flake8, pylint)
4. **Run tests** (pytest with 95% coverage requirement)
5. **Upload coverage** to Codecov

**Status**: ![CI Build](https://github.com/CSCI-GA-2820-FA25-003/products/actions/workflows/ci.yml/badge.svg)

### Continuous Deployment (Tekton Pipeline)

Automated deployment pipeline on OpenShift:

**Pipeline Tasks** (`.tekton/pipeline.yaml`):
1. **git-clone**: Clone repository
2. **pylint**: Code quality checks (runs in parallel)
3. **pytest-env**: Unit tests with PostgreSQL (runs in parallel)
4. **buildah**: Build container image
5. **deploy-image**: Deploy to Kubernetes
6. **behave**: Run BDD integration tests

**Trigger**: Webhook on push to `master` branch

**Features**:
- Parallel execution of lint and test tasks
- Automatic rollback on test failures
- BDD verification of deployed service
- Shared workspace using PersistentVolumeClaim

---

## Development Workflow

### Branching Strategy

- **master**: Production-ready code
- **feature branches**: Individual development work

### Contributing Process

1. **Assign yourself a story** from ZenHub
2. **Create a feature branch**
   ```bash
   git checkout -b feature/story-{number}
   ```
3. **Write tests first** (TDD)
4. **Implement feature**
5. **Ensure tests pass and coverage is maintained**
   ```bash
   make test
   make lint
   ```
6. **Create Pull Request**
   - Attach to corresponding ZenHub story
   - Wait for CI checks to pass
   - Request team review
7. **Merge after approval**

### Project Management

- **ZenHub**: Kanban board integrated with GitHub
- **Sprint Duration**: 2 weeks
- **Agile Practices**: Daily standups, sprint planning, retrospectives
- **Story Points**: S(3), M(5), L(8), XL(13)

---

## Team

**Products Squad** - CSCI-GA.2820-FA25-003

| Name | GitHub | Role |
|------|--------|------|
| Ashley Luo | [@luoashley](https://github.com/luoashley) | Developer |
| Zimutian Yang | [@mertinyang](https://github.com/mertinyang) | Developer |
| Yuhan Wang | [@Yuhan-W](https://github.com/Yuhan-W) | Developer |
| Shuai Huang | [@brianerd](https://github.com/brianerd) | Developer |
| Joanne Pistulli | [@Joannepistulli](https://github.com/Joannepistulli) | Developer |

---

## Project Structure

```
.
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI workflow
├── .tekton/                         # Tekton pipeline manifests
│   ├── events/                      # Event listener & trigger configs
│   │   ├── event_listener.yaml      # Tekton EventListener definition
│   │   ├── trigger_binding.yaml     # TriggerBinding mapping incoming payload
│   │   ├── trigger_template.yaml    # TriggerTemplate defining PipelineRun
│   │   └── trigger.yaml             # Trigger definition connecting all pieces
│   ├── listenerroute.yaml           # Route for EventListener service
│   ├── pipeline.yaml                # Main Tekton Pipeline definition
│   ├── productsroute.yaml           # Route for product service handling
│   ├── tasks.yaml                   # Tekton Task definitions
│   └── workspace.yaml               # Workspace & PVC configuration

├── k8s/                        # Kubernetes manifests
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   └── postgres/
├── service/                    # Application code
│   ├── __init__.py
│   ├── models.py               # Product model
│   ├── routes.py               # API endpoints (Flask-RESTX)
│   ├── config.py
│   ├── static/                 # Web UI files
│   └── common/
│       ├── cli_commands.py
│       ├── error_handlers.py
│       ├── log_handlers.py
│       └── status.py
├── tests/                      # Test suites
│   ├── test_models.py          # Unit tests for models
│   ├── test_routes.py          # Unit tests for routes
│   └── factories.py            # Test data factories
├── features/                   # BDD tests
│   ├── products.feature        # Gherkin scenarios
│   └── steps/
│       └── web_steps.py        # Selenium step definitions
├── Makefile                    # Build and deployment commands
├── Pipfile                     # Python dependencies
├── Dockerfile                  # Container image definition
└── README.md                   # This file
```

---

## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.

