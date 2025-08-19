# Cerebrum

Cerebrum is the core backend API for Graymattermetrics. It manages user authentication and crud actions for Cogspeed.

## Technology Stack

*   **Web Framework**: [FastAPI](https://fastapi.tiangolo.com/)
*   **Database ORM**: [SQLAlchemy](https://www.sqlalchemy.org/) (with `asyncio`)
*   **Testing**: [Pytest](https://docs.pytest.org/)
*   **Containerization**: [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)
*   **Code Quality**: [Black](https://github.com/psf/black), [pre-commit](https://pre-commit.com/)
*   **CI/CD**: [GitHub Actions](https://github.com/features/actions)

## Getting Started

### Installation & Setup

The recommended way to run the application for local development is using Docker Compose.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/[your-username]/cerebrum.git
    cd cerebrum
    ```

2.  **Create the environment file:**
    An environment file is required to store sensitive information like database credentials. An example file is provided.

    ```bash
    cp .env.sample .env
    ```
    You can review and modify the variables in the `.env` file if needed, but the default values are configured to work with the provided Docker Compose setup.

3.  **Build and run the containers:**
    This command will build the Docker images for the API and the database, and start them in the background.

    ```bash
    docker-compose up --build -d
    ```

The API will now be running and available at `http://localhost:6060`.

You can view the auto-generated interactive documentation (provided by FastAPI/Swagger) at [http://localhost:6060/docs](http://localhost:6060/docs).

## Running Tests

Tests are managed with Pytest and can be run inside the running API container. This ensures the tests are executed in the same environment as the application.

To run the full test suite:
```bash
docker-compose exec api pytest
```


## Code Formatting and Linting

This project uses `pre-commit` to enforce code style and quality checks before code is committed. The primary formatter is **Black**.

To enable these checks for your local development:

1.  **Install pre-commit:**
    ```bash
    pip install pre-commit
    ```

2.  **Install the Git hooks:**
    ```bash
    pre-commit install
    ```

## Continuous Integration

This repository uses **GitHub Actions** for its Continuous Integration (CI) pipeline. The workflows are defined in the `.github/workflows/` directory.

The pipeline automatically runs all tests and linting checks on every push to the `main` branch and on all pull requests.