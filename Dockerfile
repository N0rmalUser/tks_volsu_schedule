FROM python:3.12.5-slim
LABEL authors="N0rmalUser"

WORKDIR /tks_schedule

RUN apt-get update && apt-get install -y ca-certificates iputils-ping && update-ca-certificates && apt-get install -y locales
RUN localedef -i ru_RU -f UTF-8 ru_RU.UTF-8 || true

COPY app app
COPY main.py main.py
COPY config.toml config.toml
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

CMD ["python", "main.py"]