import logging
import sys

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

from poll import Poller

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


class Bot:
    def __init__(self, token, poller):
        self.poller = poller
        self.chats = []
        updater = Updater(token)
        dispatcher = updater.dispatcher
        dispatcher.add_handler(CommandHandler('start', self.start))
        dispatcher.add_handler(CommandHandler('stop', self.stop))
        # Register poller every 10s
        updater.job_queue.run_repeating(self.poll, 10)
        # Start
        updater.start_polling()
        updater.idle()

    def poll(self, context: CallbackContext) -> None:
        logger.debug('Polling...')
        global poller
        try:
            res = poller.poll()
        except Exception as e:
            logger.warning('Error fetching data: %s', e)
            return
        if len(res) > 0:
            # Broadcast to all users
            for chat in self.chats:
                context.bot.send_message(chat, text='In stock:\n' + '\n\n'.join(res))

    def start(self, update: Update, context: CallbackContext) -> None:
        logger.info('Starting for user: %s', update.effective_user.name)
        self.chats.append(update.message.chat_id)
        msg = 'Listening for changes. \nCurrently available: ' + \
              ', '.join([name for name,avail in self.poller.state.items() if avail])
        update.message.reply_text(msg)

    def stop(self, update: Update, context: CallbackContext) -> None:
        logger.info('Stopping for user %s', update.effective_user.name)
        self.chats.remove(update.message.chat_id)
        update.message.reply_text('Stopped listening for changes.')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python bot.py <TOKEN> [<GECKO_PATH>]')
        exit(1)
    token = sys.argv[1]
    global poller
    if len(sys.argv) > 2:
        poller = Poller(sys.argv[2])
    else:
        poller = Poller('geckodriver')
    logger.info('Starting...')
    Bot(token, poller)
