FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.9.2 /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy pyproject.toml and uv.lock first for better caching
COPY pyproject.toml .
COPY uv.lock .

# Install from uv locked file
RUN uv sync --locked

# Copy source code after installing dependencies
COPY . .

# Expose port
EXPOSE 8000

CMD ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
