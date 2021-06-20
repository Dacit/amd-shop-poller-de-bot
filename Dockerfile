FROM selenium/standalone-firefox:89.0

USER root

RUN apt-get update -qqy && apt-get install python3-pip -qqy

WORKDIR /bot

ENV BO_DATA_DIR="/bot"
ENV BOT_TOKEN="changeme"

COPY requirements.txt /bot

RUN pip3 install -r requirements.txt

COPY *.py /bot/

RUN CHOWN -R 1200:1200 /bot

USER 1200

CMD ["sh", "-c", "python3 /bot/bot.py $BOT_TOKEN $BOT_DATA_DIR" ]
