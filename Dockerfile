FROM python:3.10-alpine

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN mkdir /src
WORKDIR /src

COPY ./requirements.txt ./requirements.txt
RUN . /opt/venv/bin/activate && pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .
