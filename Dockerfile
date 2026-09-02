FROM astral/uv:python3.12-bookworm-slim
LABEL authors="N0rmalUser"

WORKDIR /app

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    ca-certificates iputils-ping locales \
    && rm -rf /var/lib/apt/lists/*

RUN update-ca-certificates
RUN localedef -i ru_RU -f UTF-8 ru_RU.UTF-8 || true

COPY pyproject.toml uv.lock* ./

RUN uv sync --frozen --no-cache --no-dev

COPY . .

ENV PATH="/app/.venv/bin:$PATH"