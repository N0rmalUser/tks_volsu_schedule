FROM python:3.12.5-slim
LABEL authors="N0rmalUser"

WORKDIR /schedule

ENV PYTHONUNBUFFERED=1

RUN apt-get update
RUN apt-get install -y ca-certificates iputils-ping
RUN update-ca-certificates
RUN apt-get install -y locales

RUN localedef -i ru_RU -f UTF-8 ru_RU.UTF-8 || true

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY app app
COPY main.py main.py

CMD ["python", "main.py"]