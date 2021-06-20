FROM selenium/standalone-firefox:89.0

USER root

RUN apt update -qqy && apt install python3-pip -qqy

WORKDIR /bot
RUN chown -R 1200:1200 /bot
USER 1200

ENV BO_DATA_DIR="/bot"
ENV BOT_TOKEN="changeme"

COPY --chown=1200:1200 requirements.txt /bot

RUN pip3 install -r requirements.txt

COPY --chown=1200:1200 *.py /bot/

CMD ["sh", "-c", "python3 /bot/bot.py $BOT_TOKEN $BOT_DATA_DIR" ]
