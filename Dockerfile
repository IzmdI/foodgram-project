FROM python:3.8.7

WORKDIR /code
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY . .
RUN python3 -m pip install --upgrade pip \
    && pip install -r requirements.txt --no-cache-dir \
    && rm requirements.txt \
    && python3 manage.py collectstatic --noinput
CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000