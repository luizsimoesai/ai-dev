# Docker

Docker is a platform that lets you package, distribute, and run applications in lightweight, isolated, and portable containers.
  
- https://www.docker.com/
- https://hub.docker.com/
- https://docs.docker.com/reference/dockerfile/

### Dockerfile
The Dockerfile is a configuration file that contains instructions for building a custom Docker image, defining the environment and the steps needed to run an application.

```Dockerfile
# Use the Python 3.13.5 base image with Alpine Linux
FROM python:3.13.5-alpine3.22

# Set the working directory inside the container
WORKDIR /app

# Copy only requirements.txt first.
# This allows the Docker cache to be
# leveraged: dependency installation only
# reruns when this file changes.
COPY requirements.txt .

# Install the project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files
COPY . .

```

### .dockerignore

The .dockerignore file lists file and folder patterns that should be ignored during the image build, preventing unnecessary content from being copied into the container and reducing the image size.

### docker-compose.yaml

The docker-compose.yaml is an orchestration file that declaratively describes how several Docker services should be built, configured, and run together.

```docker 
services:
  app:
    image: fastapi_app
    build: .              # Build the image from the local Dockerfile
    container_name: fastapi_app
    command: sh -c "uvicorn main:app --host 0.0.0.0 --port 8000 --reload"  # FastAPI server
    env_file:
      - .env
    volumes:
      - .:/app            # Mount the code for hot-reload in development
    ports:
      - "8000:8000"       # Expose port 8000
```

Example commands: (not in execution order, just examples)
```bash
$ docker ps
$ docker ps -a
$ docker images

$ docker compose up --build
$ docker compose up -d
$ docker compose down
```