FROM python:3.11-slim
LABEL authors="N0rmalUser"

WORKDIR /tks_schedule

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
ENV SCHEDULE_PATH=/tks_schedule/data/schedule.db
ENV DB_PATH=/tks_schedule/data/users.db
CMD ["python", "main.py"]