FROM python:3.9-alpine

ENV PYTHONUNBUFFERED 1

# Create user first (best practice)
RUN addgroup -g 1000 usergroup && \
    adduser -u 1000 -G usergroup -s /bin/sh -D adminuser

# Create app directory and set ownership
RUN mkdir /app
WORKDIR /app

# Install system dependencies
RUN apk add --update --no-cache \
    postgresql-client \
    jpeg-dev

# Install build dependencies and Python packages
COPY requirements.txt /app/
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc \
    libc-dev \
    linux-headers \
    postgresql-dev \
    musl-dev \
    zlib \
    zlib-dev \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && apk del .tmp-build-deps

# Copy application code
COPY ./app /app/
RUN chown -R adminuser:usergroup /app \
    && chmod -R 755 /app

# Switch to non-root user
USER adminuser

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.wsgi:application"]
