import collections
import datetime
import enum
import logging

ERROR_REQUEST_KEY = 'message'


def country_str(name, province=None):
    return f'{name}: {province if province else "None"}'


def names_list(arr):
    return list(map(lambda x: x.name, arr))


# 20/20/2020 -> datetime(20, 20, 2020)
def str_to_datetime(lbl: str):
    m, d, y = map(int, lbl.split('/'))

    y += 2000
    return datetime.date(y, m, d)


class ApiException(Exception):
    def __init__(self, message):
        message = f'API: {message}'
        super().__init__(message)


class ApiRequest:
    class Fields(enum.Enum):
        pass

    def __init__(self, data):
        if isinstance(data, dict):
            error_mess = data.get(ERROR_REQUEST_KEY)
            if error_mess:
                raise ApiException(error_mess)

        self.data = data
        self.parse_json()

    def parse_json(self):
        def get_attr_value(attr_path, json_object):
            if isinstance(attr_path, str):
                value = json_object.get(attr_path)
                return value if value else 0

            elif isinstance(attr_path, collections.abc.Iterable):
                pass
            else:
                # logging.critical('Unknown received api attribute type')
                raise Exception('Unknown received api type for attr: %s, %s' % (attr_path, self.__str__()))

            temp = json_object
            for i in attr_path:
                temp = temp.get(i)

            return temp

        for field in self.Fields:
            class_attr, api_attr = field.name, field.value
            self.__setattr__(class_attr, get_attr_value(api_attr, self.data))


class ListedApiRequest(ApiRequest):
    list = []

    def __init__(self, data, list_value_class: ApiRequest.__class__, sort=None):
        self.sort = sort
        self.__list_value_class = list_value_class

        self.list = []

        super().__init__(data)

    def parse_json(self):
        for elem_data in self.data:
            self.list.append(self.__list_value_class(elem_data))

        sort_func = lambda x: x.__getattribute__(self.sort.name)
        self.list.sort(key=sort_func, reverse=True)


class WorldInfo(ApiRequest):
    class Fields(enum.Enum):
        cases = 'cases'
        active = 'active'

        deaths = 'deaths'
        recovered = 'recovered'

        affected_countries = 'affectedCountries'

    # --- For autocomplete ---
    cases = None
    active = None
    deaths = None
    recovered = None
    affected_countries = None


class WorldHistorical(ApiRequest):
    class Fields(enum.Enum):
        cases_raw = 'cases'
        deaths_raw = 'deaths'
        recovered_raw = 'recovered'

    cases_raw = None
    deaths_raw = None
    recovered_raw = None

    cases_dict = None
    deaths_dict = None
    recovered_dict = None

    def parse_json(self):
        super().parse_json()

        def iter_dict(d):
            return dict((str_to_datetime(k), v) for (k, v) in d.items())

        self.cases_dict = iter_dict(self.cases_raw)
        self.deaths_dict = iter_dict(self.deaths_raw)
        self.recovered_dict = iter_dict(self.recovered_raw)


class CountryInfo(ApiRequest):
    class Fields(enum.Enum):
        name = 'country'

        cases = 'cases'
        deaths = 'deaths'

        today_cases = 'todayCases'
        today_deaths = 'todayDeaths'

        recovered = 'recovered'
        active = 'active'
        critical = 'critical'

        cases_per_million = 'casesPerOneMillion'
        deaths_per_million = 'deathsPerOneMillion'

        tests = 'tests'
        tests_per_million = 'testsPerOneMillion'

    name = None

    cases = None
    deaths = None

    today_cases = None
    today_deaths = None

    recovered = None
    active = None
    critical = None

    cases_per_million = None
    deaths_per_million = None

    tests = None
    tests_per_million = None

    death_rate = None
    flag_emoji = None
    code = None

    def get_attr(self, name):
        for field in self.Fields:
            if field.name == name:
                return self.__getattribute__(name)
        else:
            print('cant get attr from countryInfo')

    def parse_json(self):
        def flag(code):
            offset = 127462 - ord('A')
            code = code.upper()
            return chr(ord(code[0]) + offset) + chr(ord(code[1]) + offset)

        super().parse_json()
        self.code = self.data['countryInfo']['iso2']

        self.death_rate = round(self.deaths / self.cases * 100, 2)
        self.flag_emoji = flag(self.code) if self.code else None

    def __str__(self):
        return country_str(self.name)


class CountryHistorical(ApiRequest):
    class Fields(enum.Enum):
        name = 'country'
        province = 'province'

        cases_raw = 'timeline', 'cases'
        deaths_raw = 'timeline', 'deaths'
        recovered_raw = 'timeline', 'recovered'

    name = None
    province = None

    cases_raw = None
    deaths_raw = None
    recovered_raw = None

    cases_dict = None
    deaths_dict = None
    recovered_dict = None

    def parse_json(self):
        def filter_dict(d, bottom_value_border):
            items = list(d.items())
            return dict((str_to_datetime(k), v) for (k, v) in items if v > bottom_value_border // 300)

        def extend_list_with_child_values(arr):
            temp = []
            for i in arr:
                temp.extend(i)

            return temp

        super().parse_json()

        dicts = [self.cases_raw, self.deaths_raw, self.recovered_raw]

        for i in range(len(dicts)):
            if not dicts[i]:
                dicts[i] = dict()

        dicts_values = extend_list_with_child_values([list(i.values()) for i in dicts])

        maxvalue = max(dicts_values)

        self.cases_dict = filter_dict(self.cases_raw, maxvalue)
        self.deaths_dict = filter_dict(self.deaths_raw, maxvalue)
        self.recovered_dict = filter_dict(self.recovered_raw, maxvalue)

    def __str__(self):
        return country_str(self.name, province=self.province[0])


class Countries(ListedApiRequest):
    def __init__(self, data, sort: CountryInfo.Fields = CountryInfo.Fields.cases):
        super().__init__(data, CountryInfo, sort=sort)
