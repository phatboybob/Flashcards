# Use a slim Python image
FROM python:3.13-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv sync --frozen

# Copy the rest of the application
COPY . .

# Create the directory where Cloud Run will mount secrets.toml
RUN mkdir -p /app/.streamlit

# Cloud Run provides the PORT environment variable
EXPOSE 8080

CMD sh -c "uv run streamlit run flashcards.py --server.port=${PORT} --server.address=0.0.0.0"