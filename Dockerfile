FROM astral/uv:python3.14-bookworm-slim AS base

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml uv.lock ./

FROM base AS common

RUN uv sync --frozen --no-dev --no-install-project --no-default-groups

COPY app/common ./app/common
COPY app/core ./app/core
COPY app/database ./app/database
COPY app/schemas ./app/schemas
COPY app/services ./app/services

FROM base AS migrations

RUN uv sync --frozen --no-dev --no-install-project --no-default-groups --group migrations

COPY app/core ./app/core
COPY app/database ./app/database
COPY app/schemas ./app/schemas

COPY alembic ./alembic
COPY alembic.ini ./

CMD ["alembic", "upgrade", "head"]

FROM common AS seed

COPY app/seed ./app/seed

CMD ["python", "-m", "app.seed"]

FROM common AS scheduler

RUN uv sync --frozen --no-dev --no-install-project --no-default-groups --group scheduler

COPY app/workers ./app/workers

CMD ["python", "-m", "app.workers.schedule_worker"]

FROM common AS telegram

RUN uv sync --frozen --no-dev --no-install-project --no-default-groups --group telegram

COPY app/tg ./app/tg

CMD ["python", "-m", "app.tg.bot"]

FROM common AS vk

RUN uv sync --frozen --no-dev --no-install-project --no-default-groups --group vk

COPY app/vk ./app/vk

CMD ["python", "-m", "app.vk.bot"]
