FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

RUN apt update && apt install -y \
    git zip unzip openjdk-17-jdk \
    python3-pip python3-setuptools python3-wheel \
    libffi-dev libssl-dev libz-dev \
    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev \
    libjpeg-dev libfreetype6-dev libgl1-mesa-dev \
    build-essential wget curl xclip && \
    apt clean

RUN pip install --upgrade pip cython==0.29.36
RUN pip install buildozer

COPY . /app
COPY buildozer.spec .

CMD ["buildozer", "android", "debug"]
