# coding=utf-8
from __future__ import unicode_literals, absolute_import, print_function, division

from sopel.logger import get_logger
from sopel.module import commands, event, require_admin, rule
from sopel.tools import events, Identifier, SopelMemory

import random
import re

actual_topic = re.compile(r'^\[\+[a-zA-Z]+\] (.*)')
LOGGER = get_logger(__name__)


@rule('.*')
@event(events.RPL_LISTSTART, events.RPL_LIST, events.RPL_LISTEND)
def multi_event_handler(bot, trigger):
    if trigger.event == events.RPL_LISTSTART:
        bot.memory['channel_cache'] = SopelMemory()
        return LOGGER.info("Channel listing started…")
    if trigger.event == events.RPL_LIST:
        channel, _, topic = trigger.args[1:]
        bot.memory['channel_cache'][channel] = re.sub(actual_topic, r'\1', topic)
        return
    if trigger.event == events.RPL_LISTEND:
        return LOGGER.info("Channel listing finished! {} channels' topics stored."
                           .format(len(bot.memory['channel_cache'])))


@commands('chanlist')
@require_admin('Only bot admins may update the channel cache.')
def test_list(bot, trigger):
    bot.write(['LIST'])


@commands('chantopic')
def channel_topic(bot, trigger):
    if not trigger.group(2):
        return bot.say("I need a channel name.")

    channel = Identifier(trigger.group(2))
    topic = bot.memory['channel_cache'][channel]
    bot.say("Topic for {}: {}".format(channel, topic))


@commands('chanrandom', 'randchan')
def random_channel_topic(bot, trigger):
    channel = random.choice(list(bot.memory['channel_cache'].keys()))
    topic = bot.memory['channel_cache'][channel]
    msg = "Random channel for you: {}.".format(channel)
    if topic:
        msg += " The topic is: {}".format(topic)
    else:  # TODO: This never fires even though the blank topics *appear* empty
        msg += " Its topic is empty. :("
    bot.reply("Random channel for you: {}. Here's its topic: {}".format(channel, topic))