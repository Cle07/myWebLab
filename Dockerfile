# syntax = docker/dockerfile:1

FROM python:3.12-slim AS base

LABEL fly_launch_runtime="Python"

# App directory
WORKDIR /app

# Throw-away build stage
FROM base AS build

# Install build dependencies
RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y build-essential curl

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:$PATH"

# Create and use virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies directly
RUN pip install robyn jinja2 markdown markupsafe rich

# Copy application code
COPY . .

# Final stage for app image
FROM base

# Install runtime dependencies with build-essential for cc
RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y curl build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy virtual environment from build stage
COPY --from=build /opt/venv /opt/venv
COPY --from=build /root/.cargo /root/.cargo
ENV PATH="/opt/venv/bin:/root/.cargo/bin:$PATH"

# Copy built application and pre-compiled Rust code
COPY --from=build /app /app

# Start the Robyn server without compiling Rust, compiled code must be present.
EXPOSE 5000
ENV PORT=5000
CMD ["python", "-m", "robyn", "app.py", "--log-level", "WARN", "--fast", "--disable-openapi"]
