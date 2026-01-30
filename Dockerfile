FROM astral/uv:python3.14-bookworm-slim
LABEL authors="N0rmalUser"

WORKDIR /schedule

ENV PYTHONUNBUFFERED=1

RUN apt-get update
RUN apt-get install -y ca-certificates iputils-ping
RUN update-ca-certificates
RUN apt-get install -y locales

RUN localedef -i ru_RU -f UTF-8 ru_RU.UTF-8 || true

COPY pyproject.toml uv.lock* ./

RUN uv sync --frozen --no-cache --no-dev

COPY app app
COPY main.py main.py

CMD ["uv", "run", "python", "main.py"]