FROM python:3.11-slim
LABEL authors="N0rmalUser"

WORKDIR /tks_schedule

COPY requirements.txt requirements.txt
RUN apt-get update && apt-get install -y ca-certificates iputils-ping && update-ca-certificates
RUN pip install -r requirements.txt
RUN rm requirements.txt

COPY config.py config.py
COPY bot bot
COPY data data
COPY logs logs
COPY main.py main.py

ENV TIMEZONE=Europe/Moscow

ENV SCHEDULE_DB=/tks_schedule/data/schedule.db
ENV USERS_DB=/tks_schedule/data/users.db
ENV ACTIVITIES_DB=/tks_schedule/data/activities.db
ENV LOG_FILE=logs/bot.log

ENV BOT_TOKEN=6857740783:AAF2JsAWEkLra0u9PdWHBUFySonglckn_Vk
ENV ADMIN_CHAT_ID=-1001991471871

CMD ["python", "main.py"]