FROM balenalib/raspberrypi4-64-python:3.9

RUN install_packages build-essential python3-dev python3-smbus libffi-dev libjpeg-dev libopenjp2-7-dev libtiff5-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev libharfbuzz-dev libfribidi-dev libxcb1-dev libatlas-base-dev

RUN python3 -m ensurepip && \
    pip3 install --upgrade pip setuptools wheel

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "__main__.py"]
