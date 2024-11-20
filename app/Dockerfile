FROM python:3.9-alpine
ENV PYTHONUNBUFFERED 1
COPY ./requirements.txt ./requirements.txt
RUN addgroup -g 1000 usergroup && adduser -u 1000 -G usergroup -s /bin/sh -D adminuser

RUN apk add --update --no-cache postgresql-client jpeg-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev
RUN pip install --upgrade pip && pip install -r /requirements.txt
RUN pip install django django-cors-headers
RUN apk del .tmp-build-deps
RUN mkdir /app
COPY ./app /app
WORKDIR /app
RUN chown -R adminuser:usergroup /app
RUN chmod -R 755 /app 

USER adminuser

COPY . .
EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.wsgi:application"]
