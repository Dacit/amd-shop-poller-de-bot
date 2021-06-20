import logging
import sys

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters

from model import Model
from poller import Poller

logger = logging.getLogger('bot')
logger.setLevel(logging.INFO)


def help(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Available commands: /start, /stop, /status')


class Bot:
    def __init__(self, token: str, poller: Poller, model: Model):
        self.poller = poller
        self.model = model

        updater = Updater(token, workers=1)
        dispatcher = updater.dispatcher
        dispatcher.add_handler(CommandHandler('start', self.start))
        dispatcher.add_handler(CommandHandler('stop', self.stop))
        dispatcher.add_handler(CommandHandler('status', self.status))
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, help))
        # Register poller every 10s
        updater.job_queue.run_repeating(self.poll, 5, 0)
        # Start
        updater.start_polling()
        updater.idle()

    def poll(self, context: CallbackContext) -> None:
        logger.debug('Polling...')
        try:
            res = poller.poll()
        except Exception as e:
            logger.warning('Error fetching data: %s', e)
            return
        if len(res) > 0:
            msg = 'In stock:\n\n' + '\n\n'.join([f'[{name}]({url})' for name, url in res.items()])
            # Broadcast to all users
            for chat in self.model.read_chats():
                context.bot.send_message(chat, text=msg, parse_mode='MarkdownV2')

    def start(self, update: Update, context: CallbackContext) -> None:
        logger.info('Starting for user: %s', update.effective_user.name)
        self.model.add_chat(update.message.chat_id)
        msg = 'Started polling\\. Currently available:\n' + \
              '\n'.join(self.model.read_products())
        update.message.reply_markdown_v2(msg)

    def stop(self, update: Update, context: CallbackContext) -> None:
        logger.info('Stopping for user %s', update.effective_user.name)
        self.model.delete_chat(update.message.chat_id)
        update.message.reply_text('Stopped polling.')

    def status(self, update: Update, context: CallbackContext) -> None:
        if update.message.chat_id in self.model.read_chats():
            msg = f'Active. Last update: {poller.last_update}\n' + \
                '\n'.join(self.model.read_products())
        else:
            msg = 'Not active. To start, use /start'
        update.message.reply_text(msg)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python bot.py <TOKEN> [<SQLITE>]')
        exit(1)
    token = sys.argv[1]
    if len(sys.argv) > 2:
        db = sys.argv[2]
    else:
        db = 'bot.sqlite'

    model = Model(db)
    poller = Poller(model)

    logger.info('Starting...')
    Bot(token, poller, model)
