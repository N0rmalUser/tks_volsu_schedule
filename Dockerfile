FROM python:3.12.5-slim
LABEL authors="N0rmalUser"

WORKDIR /tks_schedule

RUN apt-get update && apt-get install -y ca-certificates iputils-ping && update-ca-certificates

COPY bot bot
COPY bot/config.py config.py
COPY main.py main.py
COPY config.toml config.toml
COPY pyproject.toml pyproject.toml

RUN pip install --no-cache-dir poetry
RUN poetry install --no-dev

# Почему-то не устанавливается через poetry в докере
RUN pip install toml

CMD ["python", "main.py"]