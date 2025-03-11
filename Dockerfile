FROM python:3.10.16-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONENCODING=UTF-8

WORKDIR /app

# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    git \
    g++ \
    build-essential \
    python3-dev \
    libssl-dev \
    libsasl2-dev \
    && rm -rf /var/lib/apt/lists/*

# hadolint ignore=DL3003
RUN curl -fsSL https://github.com/confluentinc/librdkafka/archive/refs/tags/v2.8.0.tar.gz -o librdkafka.tar.gz \
    && tar -xzf librdkafka.tar.gz \
    && cd librdkafka-2.8.0 \
    && ./configure --enable-ssl --enable-sasl \
    && make \
    && make install \
    && cd .. \
    && rm -rf librdkafka-2.8.0 librdkafka.tar.gz

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

COPY pyproject.emulator.toml /app/pyproject.toml

COPY ./libs /app/libs
COPY ./src/data-emulator /app/src/data-emulator

RUN uv sync --all-extras --all-groups

CMD ["uv", "run", "emulator"]
