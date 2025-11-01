FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.9.2 /uv /uvx /bin/

# Set working directory and venv path
WORKDIR /app

# Define virtual environment
ENV UV_PROJECT_ENVIRONMENT=/home/appuser/.venv
ENV PATH="/home/appuser/.venv/bin:$PATH"

# Create non-root user
RUN useradd -m appuser

# Install dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --locked

# Copy the application source code
COPY . .

# Give appuser ownership of the working directory
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose FastAPI port
EXPOSE 8000

# Use entrypoint script
ENTRYPOINT ["scripts/entrypoint.sh"]

# Default command to run the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
