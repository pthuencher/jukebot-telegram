FROM python:3

WORKDIR /jukebot

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN apt update
RUN apt install -y ffmpeg

# copy all files
COPY ./ ./

CMD [ "python", "./jukebot.py", "-d" ]
