import logging
import time
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters
from telegram.bot import Bot
from telegram.parsemode import ParseMode
from telegram.ext.dispatcher import run_async

RATE = range(1)


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
        self.updater = Updater(token=self.token, use_context=True)
        self.dp = self.updater.dispatcher
        self.bot = Bot(token=self.token)

        self.comunioscore_chatid = -394160563

        # handler to request the current points per user
        self.add_handler(command="points", handler=self.get_current_points)

        # handler to get the commands description
        self.add_handler(command="help", handler=self.help)

        # handler to get the commands description
        self.add_handler(command="cancel", handler=self.cancel)

        self.conv_handler = ConversationHandler(entry_points=[CommandHandler('updates', self.update_msg_rate)],
                                                states={RATE: [MessageHandler(Filters.text, self.rate)]},
                                                fallbacks=[CommandHandler('stop', self.stop)])
        self.dp.add_handler(self.conv_handler)

        # event handler
        self.points_summery_event_handler = None
        self.rate_event_handler = None
        self.cancel_event_handler = None

        self.last_points_sent = time.time()
        self.notify = False
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

    def register_rate_event_handler(self, func):
        """ register the rate event handler

        :param func: handler function
        """
        self.rate_event_handler = func

    def register_cancel_event_handler(self, func):
        """ register the cancel event handler

        :param func: handler function
        """
        self.cancel_event_handler = func

    def new_msg(self, text):
        """ sends new text message to the bot

        """
        try:
            self.bot.sendMessage(chat_id=self.comunioscore_chatid, text=text, parse_mode=ParseMode.MARKDOWN, timeout=20)
        except Exception as ex:
            self.logger.error(ex)

    @run_async
    def get_current_points(self, update, context):
        """ get the current points of all comunio users

        :return: msg with current points
        """
        user = update.message.from_user
        chat_id = update.message.chat_id
        self.logger.info("User {} with userid: {} requests the current points".format(user.username, user.id))

        if self.points_summery_event_handler:

            # check time
            current_time = time.time()
            send_time_diff = current_time - self.last_points_sent
            if send_time_diff > 60:
                match_day, player_standing = self.points_summery_event_handler()
                if match_day is None:
                    point_msg = "Player Ranking\n\n"
                else:
                    point_msg = "Player Ranking for match day {}\n\n".format(match_day)

                for i, (user, points) in enumerate(player_standing.items()):
                    point_msg += "*{}.* {}: {}\n".format(i+1, user, points)

                self.last_points_sent = time.time()
            else:
                point_msg = "*Don´t request the player ranking to often!!*"
        else:
            point_msg = "*No Points available!*"
            self.logger.error("Points summery event handler is not registerd!")

        context.bot.send_message(chat_id=chat_id, text=str(point_msg), parse_mode=ParseMode.MARKDOWN)

    @run_async
    def update_msg_rate(self, update, context):
        """ sets new rate for sending messages

        :return:
        """
        reply_keyboard = [['5', '10', '15', '40']]
        user = update.message.from_user
        self.logger.info("User {} with userid: {} requests new update rate".format(user.username, user.id))

        update.message.reply_text('{}, please select the desired update rate in minutes!'.format(user.username),
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

        return RATE

    def rate(self, update, context):
        """ sets the new rate to given value

        :param update: update
        :param context: context

        :return: reply message
        """
        user = update.message.from_user
        self.logger.info("User {} with userid: {} sets new update rate to {}".format(user.username, user.id, update.message.text))
        rate = update.message.text
        update.message.reply_text('Set the update rate to {} minutes! Thank you {}'.format(update.message.text, user.username),
                                  reply_markup=ReplyKeyboardRemove())

        if self.rate_event_handler:
            self.rate_event_handler(rate=rate)
        else:
            self.logger.error("No rate event handler registered!")

        return ConversationHandler.END

    @run_async
    def help(self, update, context):
        """ get the description of comunioscore

        :param bot: bot
        :param update: update

        :return: help description
        """
        chat_id = update.message.chat_id
        user = update.message.from_user
        self.logger.info("User {} with userid: {} requests the help description".format(user.username, user.id))

        help_msg = "*Welcome to ComunioScore*\n\nAvailable commands:\n/points: Get current points of comunio users\n/updates: Set new rate for updates\n/help: Usage of ComunioScore"

        context.bot.send_message(chat_id=chat_id, text=help_msg, parse_mode=ParseMode.MARKDOWN)

    def cancel(self, update, context):
        """

        :param update:
        :param context:
        :return:
        """
        chat_id = update.message.chat_id
        user = update.message.from_user
        self.logger.info("User {} with userid: {} cancels the livedata notification".format(user.username, user.id))

        if self.cancel_event_handler:
            self.cancel_event_handler(notify=self.notify)
            self.notify = not self.notify
            cancel_msg = "Notifications successfully canceled/started"
        else:
            self.logger.error("No cancel event handler registered!")
            cancel_msg = "*Notifications could not be canceled!*"

        context.bot.send_message(chat_id=chat_id, text=cancel_msg, parse_mode=ParseMode.MARKDOWN)

    def stop(self, update, context):
        """ stops the update_msg_rate conversation

        :param update: update
        :param context: context

        :return: reply text
        """
        update.message.reply_text('Bye! I hope we can talk again some day.')

        return ConversationHandler.END

if __name__ == '__main__':
    tele = ComunioScoreTelegram(token="")
    #tele.new_msg(text="was geht")
    tele.run(blocking=True)
