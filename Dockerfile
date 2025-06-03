FROM python:3.12.5-slim
LABEL authors="N0rmalUser"

WORKDIR /schedule

RUN apt-get update
RUN apt-get install -y ca-certificates iputils-ping
RUN update-ca-certificates
RUN apt-get install -y locales

RUN localedef -i ru_RU -f UTF-8 ru_RU.UTF-8 || true

COPY app app
COPY main.py main.py
COPY config.toml config.toml
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

CMD ["python", "main.py"]