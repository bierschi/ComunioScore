import logging
import configparser
from telegram.ext import Updater, CommandHandler
from ComunioScore import ROOT_DIR

config = configparser.ConfigParser()
config.read(ROOT_DIR + '/config/cfg.ini')
token = config.get('telegram', 'token')


class ComunioScoreTelegram:

    def __init__(self, token):
        self.logger = logging.getLogger('ComunioScoreApp')
        self.logger.info('create class Telegram')

        self.token = token
        self.updater = Updater(token=self.token)
        self.dp = self.updater.dispatcher

    def __del__(self):
        pass

    def run(self):
        """ runs the telegram updater

        :return:
        """
        self.updater.start_polling()
        self.updater.idle()

    def add_handler(self, command, handler):
        """ add a handler function to the dispatcher

        :param command:
        :param handler:
        """
        self.dp.add_handler(handler=CommandHandler(command=command, callback=handler))

    def send_msg(self, bot, update):
        """

        :return:
        """
        chat_id = update.message.chat_id
        bot.send_message(chat_id=chat_id, text="hallo")


if __name__ == '__main__':
    tele = ComunioScoreTelegram(token=token)
    tele.run()
