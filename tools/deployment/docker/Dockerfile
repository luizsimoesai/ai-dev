# --- EXAMPLE ---

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
