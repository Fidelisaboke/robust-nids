"""
Cache module for the backend core.
This module sets up a global Redis client for caching purposes.
It attempts to connect to the Redis server on startup and logs an error if the connection fails.
"""

import logging

import redis

from core.config import settings

app_logger = logging.getLogger("uvicorn.error")

redis_client = None

try:
    # Get Redis URL from settings or use default
    redis_url = getattr(settings, "REDIS_URL", "redis://localhost:6379/0")

    # Create the global Redis client
    # decode_responses=True makes it return strings instead of bytes
    redis_client = redis.from_url(redis_url, decode_responses=True)

    # Test the connection on startup
    redis_client.ping()
    app_logger.info(f"Connected to Redis at {redis_url}")

except redis.exceptions.ConnectionError:
    app_logger.error(f"FATAL: Could not connect to Redis at {redis_url}.")
    app_logger.error("Please ensure the Redis server is running: `sudo service redis-server start`")
    redis_client = None
