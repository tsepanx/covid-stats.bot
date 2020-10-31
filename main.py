import telegram as tg

from tglib.bot import Bot
from tglib.classes.command import Command
from tglib.classes.chat import ChatHandler
from tglib.types import MESSAGE_TYPES

from api.classes import CountryInfo
from api.request import Request

from message_objects import WorldMessage, CountryMessage
from parsers import country_command_usage


def send_country_by(chat, country_name: str):
    msg = CountryMessage(country_name, draw_graph=True)
    msg.send(chat)


def send_country_class(chat, country_class: CountryInfo):
    send_country_by(chat, country_class.name)


def world_data(chat: ChatHandler, _):
    msg = WorldMessage(20, sort=CountryInfo.Fields.cases)
    msg.send(chat)


def top_countries(chat: ChatHandler, _):
    countries_cnt = 3

    req = Request.countries()
    for i in range(countries_cnt - 1):
        send_country_class(chat, country_class=req.list[i])


def certain_country(chat: ChatHandler, _):
    chat.send_message(country_command_usage())


class MyChatHandler(ChatHandler):
    class CommandsEnum(ChatHandler.CommandsEnum):
        world = ('Statistics for whole world', world_data)
        top = ('Statistics for first 3 countries with most cases', top_countries)
        country = ('Statistics for a certain country', certain_country)

    def reply(self, update: tg.Update, msg_type: MESSAGE_TYPES):
        super().reply(update, msg_type)

        if msg_type == MESSAGE_TYPES.COMMAND:
            cmd = Command(self, update)

            if cmd.name in self.existing_commands_list:
                return

            country_name = cmd.name.capitalize()
            send_country_by(self, country_name)


if __name__ == '__main__':
    Bot(_chat_class=MyChatHandler).main()
