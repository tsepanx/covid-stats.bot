from api.request import Request
from api.classes import CountryInfo
from plots import Draw

from parsers import countries_table, world_info, country_info


class MessageObject:
    def __init__(self):
        self.msg_kwargs = {
            'parse_mode': 'Markdown',
            'caption': str(self),
            'text': str(self)
        }

    def send(self, chat):
        return chat.send_message(**self.msg_kwargs)

    def __str__(self):
        return ''


class ImageMessageObject(MessageObject):
    def send(self, chat):
        if self.msg_kwargs.get('photo'):
            return chat.send_photo(**self.msg_kwargs)
        return chat.send_message(**self.msg_kwargs)


class GraphMessageObject(ImageMessageObject):
    def __init__(self, draw_func, drawable_object, draw_graph=True):
        super().__init__()

        if draw_graph:
            self.plot_filename = draw_func(drawable_object)
            if self.plot_filename:
                self.msg_kwargs['photo'] = open(self.plot_filename, 'rb')


class WorldMessage(GraphMessageObject):
    def __init__(self, first_countries=None, draw_graph=True, sort=CountryInfo.Fields.cases):
        self.__info = Request.world_info()
        self.__historical = Request.world_historical()
        self.__countries = Request.countries(sort=sort)

        self.sort = sort.name
        self.first_countries = first_countries

        super(WorldMessage, self).__init__(Draw.world_historical, self.__historical, draw_graph=draw_graph)

    def __str__(self):
        return world_info(self.__info) + countries_table(self.__countries, self.first_countries, self.sort)


class CountryMessage(GraphMessageObject):
    def __init__(self, name, draw_graph=False):
        self.__info = Request.country_info(name)
        self.__historical = Request.country_historical(self.__info.name)

        super(CountryMessage, self).__init__(Draw.country_historical, self.__historical, draw_graph=draw_graph)

    def __str__(self):
        return country_info(self.__info)
