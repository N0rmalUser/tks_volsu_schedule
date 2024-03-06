FROM python:3.11-slim
LABEL authors="N0rmalUser"

WORKDIR /tks_schedule

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY config.py config.py
COPY bot bot
COPY data data
COPY logs logs
COPY main.py main.py

ENV SCHEDULE_DB=/tks_schedule/data/schedule.db
ENV USERS_DB=/tks_schedule/data/users.db
CMD ["python", "main.py"]