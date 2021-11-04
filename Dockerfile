FROM python:3

WORKDIR /jukebot

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# copy all files
COPY ./ ./

CMD [ "python", "./jukebot.py", "-d" ]