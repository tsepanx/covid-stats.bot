import enum

import requests

from .classes import WorldInfo, WorldHistorical, CountryHistorical, Countries, CountryInfo


class UrlHandling:
    BASE_API_URL = "https://corona.lmao.ninja/"

    class Endpoints:
        ALL = 'v2/all/'
        HISTORY = 'v2/historical/'
        COUNTRIES = 'v2/countries/'


class Request:
    class ApiRequestEnum(enum.Enum):
        world = (
            lambda _: 'v2/all',
            WorldInfo
        )
        world_historical = (
            lambda _: 'v2/historical/all?lastdays=all',
            WorldHistorical
        )
        country_historical = (
            lambda country: f'v2/historical/{country}?lastdays=all',
            CountryHistorical
        )
        country_info = (
            lambda country: f'v2/countries/{country}',
            CountryInfo
        )
        countries = (
            lambda _: f'v2/countries/',
            Countries
        )

    @staticmethod
    def __get_request(get_url, **kwargs):
        print(get_url)
        return requests.get(get_url, kwargs).json()

    @staticmethod
    def __get_api_request(route, **params):
        return Request.__get_request(UrlHandling.BASE_API_URL + route, **params)

    @staticmethod
    def __get_api_request_parsed(request: ApiRequestEnum, country=None, **params):
        route_func = request.value[0]
        parser_class = request.value[1]

        data = Request.__get_api_request(route_func(country))

        return parser_class(data, **params)

    @staticmethod
    def world_info() -> WorldInfo:
        return Request.__get_api_request_parsed(Request.ApiRequestEnum.world)

    @staticmethod
    def world_historical() -> WorldHistorical:
        return Request.__get_api_request_parsed(Request.ApiRequestEnum.world_historical)

    @staticmethod
    def country_historical(name) -> CountryHistorical:
        return Request.__get_api_request_parsed(Request.ApiRequestEnum.country_historical, name)

    @staticmethod
    def countries(sort: CountryInfo.Fields = CountryInfo.Fields.cases) -> Countries:
        return Request.__get_api_request_parsed(Request.ApiRequestEnum.countries, sort=sort)

    @staticmethod
    def country_info(name) -> CountryInfo:
        return Request.__get_api_request_parsed(Request.ApiRequestEnum.country_info, country=name)
