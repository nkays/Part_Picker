# Set the python version as a build-time argument
ARG PYTHON_VERSION=3.12-slim-bullseye
FROM python:${PYTHON_VERSION}

# Set Python-related environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install OS dependencies
RUN apt-get update && apt-get install -y \
    curl \
    # for postgres
    libpq-dev \
    # for Pillow
    libjpeg-dev \
    # for CairoSVG
    libcairo2 \
    # other
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -Ls https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Create project directory
# RUN mkdir -p /code
WORKDIR /code

# Copy dependency files FIRST (for Docker layer caching)
COPY pyproject.toml uv.lock /code/

# Install Python dependencies
RUN uv sync --frozen --no-dev

# Copy project code
COPY ./src /code

# Copy entrypoint script
COPY ./boot/docker-run.sh /opt/docker-run.sh
RUN chmod +x /opt/docker-run.sh

# Collect static files
RUN uv run python manage.py collectstatic --noinput

# Clean up apt cache
RUN apt-get remove --purge -y \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

CMD ["/opt/docker-run.sh"]