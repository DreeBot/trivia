# syntax=docker/dockerfile:1

FROM python:3.11-slim
WORKDIR /trivia/src
COPY requirements.txt .
EXPOSE 5000
EXPOSE 5001
RUN bash -c "python -m venv /trivia/venv --system-site-packages && source /trivia/venv/bin/activate && pip3 install -r requirements.txt"
COPY *.py .
COPY *.js .
COPY *.html .
COPY *.png .
