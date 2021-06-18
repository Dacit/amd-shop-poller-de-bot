import logging
import sys

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters

from poll import Poller

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def help(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Available commands: /start, /stop')


class Bot:
    def __init__(self, token, poller):
        self.poller = poller
        self.chats = []
        updater = Updater(token)
        dispatcher = updater.dispatcher
        dispatcher.add_handler(CommandHandler('start', self.start))
        dispatcher.add_handler(CommandHandler('stop', self.stop))
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
            for chat in self.chats:
                context.bot.send_message(chat, text=msg, parse_mode='MarkdownV2')

    def start(self, update: Update, context: CallbackContext) -> None:
        logger.info('Starting for user: %s', update.effective_user.name)
        self.chats.append(update.message.chat_id)
        msg = 'Started polling\\. Currently available:\n' + \
              '\n'.join([name for name, avail in self.poller.state.items() if avail])
        update.message.reply_markdown_v2(msg)

    def stop(self, update: Update, context: CallbackContext) -> None:
        logger.info('Stopping for user %s', update.effective_user.name)
        self.chats.remove(update.message.chat_id)
        update.message.reply_text('Stopped polling.')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python bot.py <TOKEN>')
        exit(1)
    token = sys.argv[1]
    poller = Poller()
    logger.info('Starting...')
    Bot(token, poller)
