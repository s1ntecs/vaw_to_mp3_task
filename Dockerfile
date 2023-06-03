FROM python:3.10

RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app

ADD requirements.txt /app

RUN pip install --upgrade pip && pip install -r /app/requirements.txt

EXPOSE 8080

COPY ./ /app

CMD ["python", "main.py"]
