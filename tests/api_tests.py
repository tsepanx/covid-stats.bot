import unittest

from api.classes import CountryHistorical, CountryInfo
from api.request import Request


class ApiRequestsTests(unittest.TestCase):
    TEST_COUNTRIES = ['Russia']

    def assert_country_info(self, country: CountryInfo):
        self.assertLess(country.deaths, country.cases + country.recovered)

    def assert_historical_dicts(self, request):
        dicts = [
            request.cases_dict,
            request.deaths_dict,
            request.recovered_dict
        ]
        print(str(request), map(len, dicts))
        self.assertNotIn(None, dicts)

    def assert_country_historical(self, country_historical: CountryHistorical):
        self.assert_historical_dicts(country_historical)

    def test_world_historical(self):
        req = Request.world_historical()
        self.assert_historical_dicts(req)

    def test_country_historical_request(self):
        for country_name in self.TEST_COUNTRIES:
            request = Request.country_historical(country_name)
            self.assert_country_historical(request)

    def test_world_info_request(self):
        req = Request.world_info()
        self.assertGreater(req.cases + req.recovered, 2 * 10 ** 6)

    def test_country_info_request(self):
        for country_name in self.TEST_COUNTRIES:
            req = Request.country_info(country_name)
            self.assert_country_info(req)

    def test_countries_request(self):
        req = Request.countries()
        for country_info in req.list:
            self.assert_country_info(country_info)


if __name__ == '__main__':
    unittest.main()
