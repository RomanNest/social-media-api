FROM python:3.11.10-alpine3.19
LABEL maintainer="rom.puh@gmail.com"

ENV PYTHONUNBUFFERED 1

WORKDIR app/

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
RUN mkdir -p /vol/web/media

RUN adduser \
         --disabled-password \
         --no-create-home \
         django-user

RUN chown -R django-user:django-user /vol/
RUN chmod -R 755 /vol/web/

USER django-user
