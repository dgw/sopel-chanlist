# coding=utf-8
from __future__ import unicode_literals, absolute_import, print_function, division

from sopel.logger import get_logger
from sopel.module import commands, event, require_admin, rule
from sopel.tools import events, Identifier, SopelMemory

import random
import re

# This regex was tested against Rizon's LIST output.
# You might need to play around with it to get sensible
# output from your favorite network.
actual_topic = re.compile(r'^\[\+[a-zA-Z]+\] (.*)')
LOGGER = get_logger(__name__)


@rule('.*')
@event(events.RPL_LISTSTART, events.RPL_LIST, events.RPL_LISTEND)
def channel_cache_update_handler(bot, trigger):
    if trigger.event == events.RPL_LISTSTART:
        # Do stuff that should happen before any list items arrive,
        # such as (in this case) clearing the cache so it can be refilled.
        bot.memory['channel_cache'] = SopelMemory()
        return LOGGER.info("Channel listing started…")
    if trigger.event == events.RPL_LIST:
        # Every channel in the list will pass through this section.
        # Make this code efficient, because it might be called thousands of times.
        # For RPL_LIST, arg 1 is the channel name, arg 2 is the number of users in
        # that channel, and arg 3 is the topic.
        channel, _, topic = trigger.args[1:]
        # Rizon prepends the modes to the topic as e.g. [+nt], so the cleanup regex
        # from above is used to remove that before storing in the cache.
        bot.memory['channel_cache'][channel] = re.sub(actual_topic, r'\1', topic)
        return
    if trigger.event == events.RPL_LISTEND:
        # If you're listing to a file, for example, you'd close it here.
        # This sample code just sends a log message (though Sopel won't
        # output info messages by default).
        return LOGGER.info("Channel listing finished! {} channels' topics stored."
                           .format(len(bot.memory['channel_cache'])))


@commands('chanlist')
@require_admin('Only bot admins may update the channel cache.')
def channel_cache_command(bot, trigger):
    # bot.write() expects an iterable as input.
    # Giving it 'LIST' instead of ['LIST'] will make the bot iterate through
    # the string character-by-character, sending 'L I S T'. Mind this one.
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