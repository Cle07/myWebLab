# syntax = docker/dockerfile:1

FROM python:3.12-slim AS base

LABEL fly_launch_runtime="Python"

# App directory
WORKDIR /app

# Throw-away build stage
FROM base AS build

# Install build dependencies
RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y build-essential

# Create and use virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies directly
RUN pip install robyn jinja2 markdown markupsafe

# Copy application code
COPY . .

# Final stage for app image
FROM base

# Install runtime dependencies
RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy virtual environment from build stage
COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy built application
COPY --from=build /app /app

# Start the Robyn server with debug flags
EXPOSE 5000
ENV PORT=5000
CMD ["python", "app.py", "--log-level", "DEBUG", "--compile-rust-path", ".", "--fast"]
