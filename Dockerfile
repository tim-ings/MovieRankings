FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.8

WORKDIR /app

COPY ./requirements.txt ./
RUN python -m pip install -r requirements.txt

COPY ./uwsgi.ini ./
COPY ./data.db ./
COPY ./nginx.conf /etc/nginx/conf.d/nginx.conf

COPY ./movie_rankings ./