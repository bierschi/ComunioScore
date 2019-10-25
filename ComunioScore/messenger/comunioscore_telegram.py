import logging
import configparser
from telegram.ext import Updater, CommandHandler
from telegram.bot import Bot
from ComunioScore import ROOT_DIR

config = configparser.ConfigParser()
config.read(ROOT_DIR + '/config/cfg.ini')
token = config.get('telegram', 'token')


class ComunioScoreTelegram:

    def __init__(self, token):
        self.logger = logging.getLogger('ComunioScoreApp')
        self.logger.info('create class ComunioScoreTelegram')

        self.token = token
        self.updater = Updater(token=self.token)
        self.dp = self.updater.dispatcher

        self.bot = Bot(token=self.token)
        self.comunioscore_chatid = -394160563

    def __del__(self):
        pass

    def run(self):
        """ runs the telegram updater

        """
        self.updater.start_polling()
        self.updater.idle()

    def add_handler(self, command, handler):
        """ add a handler function to the dispatcher

        :param command: command msg
        :param handler: handler function to execute
        """
        self.dp.add_handler(handler=CommandHandler(command=command, callback=handler))

    def send_msg(self, bot, update):
        """

        :return:
        """
        chat_id = update.message.chat_id
        print(chat_id)
        bot.send_message(chat_id=chat_id, text="hallo")

    def new_msg(self, text):
        """ new text message for the bot

        """
        self.logger.info("send new message")
        self.bot.sendMessage(chat_id=self.comunioscore_chatid, text=text)

    def new_photo(self):
        """

        :return:
        """
        self.bot.sendPhoto(chat_id=self.comunioscore_chatid)
        pass

if __name__ == '__main__':
    tele = ComunioScoreTelegram(token=token)
    #tele.add_handler('start', tele.send_msg)
    tele.new_msg(text="was geht")
    tele.run()
