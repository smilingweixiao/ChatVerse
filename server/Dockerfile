FROM python:3.9.6 as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update -y &&\
    apt-get install libasound-dev libportaudio2 libportaudiocpp0 portaudio19-dev -y &&\
    rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

COPY . .

EXPOSE 5000
EXPOSE 3000

CMD ["python", "app.py"]