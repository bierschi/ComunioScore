import time
import logging
import random
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters
from telegram.bot import Bot
from telegram.parsemode import ParseMode
from telegram.ext.dispatcher import run_async

RATE = range(1)
NOTIFY = range(1)


class ComunioScoreTelegram:
    """ class ComunioScoreTelegram to send updates to the Telegram group

    USAGE:
            cstelegram = ComunioScoreTelegram(token='')
            cstelegram.new_msg()

    """
    def __init__(self, token, chat_id):
        self.logger = logging.getLogger('ComunioScore')
        self.logger.info('Create class ComunioScoreTelegram')

        self.token = token
        self.updater = Updater(token=self.token, use_context=True)
        self.dp = self.updater.dispatcher
        self.bot = Bot(token=self.token)

        self.comunioscore_chatid = chat_id

        self.notify = True
        self.last_points_sent = time.time()

        # handler to request the current points per user
        self.add_handler(command="ranking", handler=self.get_current_points)

        # handler to get the commands description
        self.add_handler(command="help", handler=self.help)

        # conversation handler for the update msg rate
        self.msg_rate_conv_handler = ConversationHandler(entry_points=[CommandHandler('updates', self.update_msg_rate)],
                                                         states={RATE: [MessageHandler(Filters.text, self.rate)]},
                                                         fallbacks=[CommandHandler('stop', self.stop)])

        # conversation handler for the notifications
        self.notify_conv_handler = ConversationHandler(entry_points=[CommandHandler('notify', self.notification)],
                                                       states={NOTIFY: [MessageHandler(Filters.text, self.notify_on_off)]},
                                                       fallbacks=[CommandHandler('stop', self.stop)])

        self.dp.add_handler(self.msg_rate_conv_handler)
        self.dp.add_handler(self.notify_conv_handler)

        # event handler
        self.points_summery_event_handler = None
        self.rate_event_handler = None
        self.notify_event_handler = None

        # msg list
        self.ranking_replies = ['*{user}*, don´t request the player ranking to often!!',
                                '*{user}*, wtf are you doing here!!',
                                '*{user}*, come on dude, are you kidding me?',
                                '*{user}*, bitches don´t get any ranking here!',
                                '*{user}*, fuck off bastard!']

        self.notification_replies = ['*{user}*, you don´t have the permission to turn on/off the notifications!',
                                     '*{user}*, wtf are you doing here!!',
                                     '*{user}*, come on dude, are you kidding me?',
                                     '*{user}*, bitches here, too many bitches here!',
                                     '*{user}*, fuck off bastard!']

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

    def register_notify_event_handler(self, func):
        """ register the cancel event handler

        :param func: handler function
        """
        self.notify_event_handler = func

    def new_msg(self, text):
        """ sends new text message to the bot

        """

        try:
            self.bot.sendMessage(chat_id=self.comunioscore_chatid, text=text, parse_mode=ParseMode.MARKDOWN, timeout=20)
        except Exception as ex:
            self.logger.error(ex)

    @run_async
    def get_current_points(self, update, context):
        """ get the current player ranking of all comunio users

        :return: msg with current player ranking
        """

        user = update.message.from_user
        chat_id = update.message.chat_id
        self.logger.info("User {} with userid: {} requests the current player ranking".format(user.username, user.id))

        if self.points_summery_event_handler:

            current_time = time.time()
            send_time_diff = current_time - self.last_points_sent
            # send points only after 30 sec has passed
            if send_time_diff > 30:
                match_day, player_standing = self.points_summery_event_handler()
                self.logger.info("Sending data from match day: {} with player standing: {}".format(match_day, player_standing))
                if match_day is None:
                    point_msg = "Player Ranking\n\n"
                else:
                    point_msg = "Player Ranking for match day {}\n\n".format(match_day)

                for i, (user, points) in enumerate(player_standing.items()):
                    point_msg += "*{}.* {}: {}\n".format(i+1, user, points)

                self.last_points_sent = time.time()
            else:
                msg = random.choice(self.ranking_replies)
                point_msg = msg.format(user=user.username)
        else:
            point_msg = "*No Points available!*"
            self.logger.error("Points summery event handler is not registerd!")

        context.bot.send_message(chat_id=chat_id, text=point_msg, parse_mode=ParseMode.MARKDOWN)

    @run_async
    def update_msg_rate(self, update, context):
        """ sets new rate for sending messages

        :return: RATE handler
        """
        reply_keyboard = [['5', '10', '15', '20', '40']]
        user = update.message.from_user
        self.logger.info("User {} with userid: {} requests new update rate".format(user.username, user.id))

        update.message.reply_markdown('*{}*, please select the desired update rate! (Rates are in minutes)'.format(user.username),
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

        if self.rate_event_handler:

            rate = update.message.text
            update.message.reply_markdown('Thank you *{}*! I will change the update rate to *{}* minutes'.format(user.username, update.message.text),
                                          reply_markup=ReplyKeyboardRemove())

            self.rate_event_handler(rate=rate)
        else:
            update.message.reply_markdown('Oh sry *{}*! Errors have occured, so i can not change the update rate. Please try it again later'.format(user.username),
                                          reply_markup=ReplyKeyboardRemove())
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

        help_msg = "*Welcome to ComunioScore*\n\nAvailable commands:\n" \
                   "/ranking: Get the current comunio user ranking\n" \
                   "/updates: Set new rate for update msg\n" \
                    "/notify: Turn on/off the notifications\n" \
                   "/help: Usage of ComunioScore"

        context.bot.send_message(chat_id=chat_id, text=help_msg, parse_mode=ParseMode.MARKDOWN)

    def notification(self, update, context):
        """ Notification conversation handler start point

        :param update: update
        :param context: context

        :return: NOTIFY
        """
        reply_keyboard = [['ON', 'OFF']]

        user = update.message.from_user
        self.logger.info("User {} with userid: {} requests the notify command".format(user.username, user.id))

        update.message.reply_markdown('*{}*, do you want to turn on or off the notifications?'.format(user.username),
                                      reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

        return NOTIFY

    def notify_on_off(self, update, context):
        """ turns the notification on or off

        :param update: update
        :param context: context

        :return: reply message
        """
        user = update.message.from_user
        self.logger.info("User {} with userid: {} requests the livedata notification".format(user.username, user.id))

        if self.notify_event_handler:
            on_or_off = update.message.text

            if user.id == 755923632:
                if on_or_off == 'ON':
                    if self.notify:
                        notify_msg = "*{}*, the notifications already turned on!".format(user.username)
                    else:
                        self.notify_event_handler(notify=True)
                        self.notify = True
                        notify_msg = "Thank you *{}*, i will turn on the notifications!".format(user.username)
                else:
                    if self.notify:
                        self.notify_event_handler(notify=False)
                        self.notify = False
                        notify_msg = "Thank you *{}*, i will turn off the notifications!".format(user.username)
                    else:
                        notify_msg = "*{}*, the notifications already turned off!".format(user.username)
            else:
                msg = random.choice(self.notification_replies)
                notify_msg = msg.format(user.username)
        else:
            self.logger.error("No cancel event handler registered!")
            notify_msg = "Oh sry *{}*! Errors have occured. Please try it again later".format(user.username)

        update.message.reply_markdown(notify_msg, reply_markup=ReplyKeyboardRemove())

        return ConversationHandler.END

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
