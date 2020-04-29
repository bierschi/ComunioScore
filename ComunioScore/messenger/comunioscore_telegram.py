import logging
from telegram.ext import Updater, CommandHandler
from telegram.bot import Bot
from telegram.parsemode import ParseMode
from telegram.ext.dispatcher import run_async


class ComunioScoreTelegram:
    """ class ComunioScoreTelegram to send updates to the Telegram group

    USAGE:
            cstelegram = ComunioScoreTelegram()
            cstelegram.new_msg()

    """
    def __init__(self, token):
        self.logger = logging.getLogger('ComunioScore')
        self.logger.info('Create class ComunioScoreTelegram')

        self.token = token
        self.updater = Updater(token=self.token)
        self.dp = self.updater.dispatcher

        self.bot = Bot(token=self.token)
        self.comunioscore_chatid = -394160563

        self.user_id = {
            'bierschi': 755923632,
        }

        # handler to request the current points per user
        self.add_handler(command="points", handler=self.get_current_points)

        # handler to update the msg update rate per user
        self.add_handler(command="msg_rate", handler=self.update_msg_rate)

        self.points_summery_event_handler = None

    def run(self, blocking=False):
        """ runs the telegram updater

        """
        self.updater.start_polling()
        if blocking:
            self.updater.idle()

    def add_handler(self, command, handler):
        """ add a handler function to the dispatcher

        :param command: command msg
        :param handler: handler function to execute
        """
        self.dp.add_handler(handler=CommandHandler(command=command, callback=handler))

    def register_points_summery_event_handler(self, func):
        """ current points event handler

        :param func: handler function
        """
        self.points_summery_event_handler = func

    def new_msg(self, text):
        """ new text message for the bot

        """
        #self.logger.info("Send new message to comunioscore group")
        self.bot.sendMessage(chat_id=self.comunioscore_chatid, text=text, parse_mode=ParseMode.MARKDOWN)

    @run_async
    def get_current_points(self, bot, update):
        """

        :return:
        """
        chat_id = update.message.chat_id
        user_id = update.effective_user.id
        self.logger.info("Userid: {} requests the current points".format(user_id))

        if self.points_summery_event_handler:
            point_msg = self.points_summery_event_handler()

        else:
            point_msg = "No Points available!"
            self.logger.error("Points summery event handler is not registerd!")

        bot.send_message(chat_id=chat_id, text=str(point_msg), parse_mode=ParseMode.MARKDOWN)

    def update_msg_rate(self, bot, update):
        """

        :return:
        """
        chat_id = update.message.chat_id
        user_id = update.effective_user.id
        self.logger.info("Userid: {} updates the msg rate".format(user_id))

        bot.send_message(chat_id=chat_id, text="set new msg rate to", parse_mode=ParseMode.MARKDOWN)

    def map_comunio_user_with_user_id(self, comunio_user, user_id):
        """

        :param comunio_user:
        :param user_id:
        :return:
        """
        pass

if __name__ == '__main__':
    tele = ComunioScoreTelegram(token="")
    #tele.new_msg(text="was geht")
    tele.run()
