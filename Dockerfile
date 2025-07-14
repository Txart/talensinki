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

RUN uv sync --locked

# Expose port if your app serves HTTP
EXPOSE 8000

# Command to run your application
CMD ["uv", "run", "talensinki"]
