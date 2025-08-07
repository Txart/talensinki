# Use Python base image
FROM python:3.13-slim-bookworm
# install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory inside container
WORKDIR /app

# Install system dependencies that might be needed for your RAG app
RUN apt update && apt install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the project into the image
ADD . /app

# Sync dependencies and install the package
RUN uv sync --locked

# Install the package in development mode
RUN uv pip install -e .

# Expose port if your app serves HTTP
EXPOSE 8000

# Command to run your application
CMD ["uv", "run", "talensinki"]

# Label to be able to identify the docker image
LABEL project="talensinki"
