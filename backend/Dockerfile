FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.9.2 /uv /uvx /bin/

# Set working directory and venv path
WORKDIR /app

# Create a non-root user
RUN useradd -m appuser

# Define virtual environment path outside of the working directory
ENV UV_PROJECT_ENVIRONMENT=/home/appuser/.venv
ENV VENV_PATH=/home/appuser/.venv
ENV PATH="$VENV_PATH/bin:$PATH"

# Give appuser ownership of the working directory and the new venv
RUN chown -R appuser:appuser /app

# Copy and install Python dependencies
COPY --chown=appuser:appuser pyproject.toml uv.lock ./

# Switch to non-root user
USER appuser

# Install dependencies in a virtual environment
RUN uv sync --locked

# Copy the application source code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Use entrypoint script
ENTRYPOINT ["scripts/entrypoint.sh"]

# Default command to run the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
