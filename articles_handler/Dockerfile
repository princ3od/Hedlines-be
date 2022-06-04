# Use Python38
FROM python:3.8
# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

ENV PORT 8080

COPY . ./

RUN apt update
RUN pip install -r requirements.txt

CMD exec gunicorn --preload --bind :$PORT --workers 1 --timeout 0 --threads 4 app:app