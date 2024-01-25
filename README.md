# Django Project Setup and Run

This guide will walk you through the steps to set up and run a Django project using Docker Compose.

## Prerequisites

Before getting started, make sure you have the following installed on your machine:

- Docker: [Install Docker](https://docs.docker.com/get-docker/)
- Docker Compose: [Install Docker Compose](https://docs.docker.com/compose/install/)

## Getting Started

1. Clone the repository:

    ```shell
    git clone https://github.com/nilesh05apr/CreditApp.git
    ```

2. Navigate to the project directory:

    ```shell
    cd CreditApp
    ```

3. Build the Docker images:

    ```shell
    docker-compose build
    ```

4. Start the Docker containers:

    ```shell
    docker-compose up -d
    ```

5. Apply database migrations:

    ```shell
    docker-compose exec web python manage.py migrate
    ```

6. Create a superuser (optional):

    ```shell
    docker-compose exec web python manage.py createsuperuser
    ```

7. Access the Django application:

    Open your web browser and visit [http://localhost:8000](http://localhost:8000)

