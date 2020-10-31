from api.classes import CountryInfo


def base_parser(lines):
    return '\n'.join(lines)


def world_info(world):
    lines = [
        "` :: World :: `",
        f"Cases: *{world.cases}*",
        f"Deaths: {world.deaths}",
        f"Recovered: {world.recovered}",
        '',
        f'Affected Countries: {world.affected_countries}'
        '',
        '',
    ]

    return base_parser(lines)


def countries_table(countries, rows=None, sorted_by=CountryInfo.Fields.cases.name):
    def limit_country_name(name):
        if len(name) > 15:
            return name[:12].strip() + '...'
        return name

    table_format = "`{:<3} {:<15} {:<6}` /{:<2}"

    data = [table_format.format("N", "Name", sorted_by.capitalize(), 'country')]

    for i in range(rows if rows is not None else len(countries.list)):
        cntry: CountryInfo = countries.list[i]
        flag = cntry.flag_emoji if cntry.flag_emoji else ' '
        code = cntry.code.lower() if cntry.code else ' '

        cntry.name = limit_country_name(cntry.name)

        row = [i + 1, f'{flag} {cntry.name}', cntry.get_attr(sorted_by), code]
        row = [k if k is not None else '' for k in row]

        data.append(table_format.format(*row))

    return base_parser(data)


def country_info(country: CountryInfo):
    lines = [
        f"{country.flag_emoji} `{country.name}` {country.flag_emoji}",
        '',
        f'Cases: *{country.cases} (+{country.today_cases})*',
        f'Deaths: {country.deaths} (+{country.today_deaths})',
        f'Recovered: {country.recovered}',
        '',
        f'Death rate: {country.death_rate}%',
        '',
        f'Cases per 1 Million: *{country.cases_per_million}*',
        f'Deaths per 1 Million: {country.deaths_per_million}',
        '',
        f'Tests: *{country.tests}*',
        f'Tests per 1 Million: {country.tests_per_million}',

    ]

    return base_parser(lines)


def country_command_usage():
    lines = [
        'Usage: /<country_name>',
        'Example: /china, /italy, /russia, etc.',
        '',
        'Usage 2: /<country_code>',
        'Example: /cn, /it, /ru, etc.'
    ]

    return base_parser(lines)
