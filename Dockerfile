# Download python 3.11 image
FROM python:3.11-slim

# Set the working directory to /src
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy Poetry's definition files
COPY pyproject.toml poetry.lock /app/
COPY api /app/api
COPY alembic.ini /app/
COPY alembic /app/alembic
COPY .env /app/

# Disable virtual environments created by Poetry
RUN poetry config virtualenvs.in-project true

# Install dependencies using Poetry
RUN poetry install --only main

# Expose port 80 for fast api, 8501 for streamlit 
EXPOSE 80
EXPOSE 8501