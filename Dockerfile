FROM python:3.11-slim
LABEL authors="N0rmalUser"

WORKDIR /tks_schedule

RUN apt-get update && apt-get install -y ca-certificates iputils-ping && update-ca-certificates

COPY bot bot
RUN pip install -r bot/requirements.txt
RUN rm bot/requirements.txt
COPY config.py config.py
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