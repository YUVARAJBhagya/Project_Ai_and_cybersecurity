# Production Dockerfile for A4S Eval


# ----- BASE
# Base stage with common components
FROM python:3.12-slim-bookworm AS base

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:0.4.9 /uv /bin/uv


# ----- Builder
# Builder stage for dependencies and compilation
FROM base AS builder

# Enable bytecode compilation and copy linking
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

WORKDIR /app

# Copy dependency files
COPY uv.lock pyproject.toml /app/

# Install production dependencies with caching
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --no-install-project --no-dev

# Copy application code
COPY . /app

# Install project in production mode
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --no-dev


# ----- Test
# Test stage for running tests and linters
FROM builder AS test

# Install test and development dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --dev

ENV PATH="/app/.venv/bin:$PATH"

# Run tests (example with pytest)
CMD ["pytest", "--maxfail=1", "--disable-warnings"]


# Final stage for runtime
FROM builder AS prod

# Copy built application from builder
COPY --from=builder /app /app

WORKDIR /app

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Set up entrypoint script
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]

# Expose API port
EXPOSE 8000

# Start FastAPI application
CMD ["uvicorn", "a4s_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
