import os

import matplotlib.pyplot as plt
import datetime

from api.classes import CountryHistorical, WorldHistorical

STATIC_PATH = os.path.join(os.path.dirname(__file__), 'static')


class Draw:
    @staticmethod
    def __get_request_drawable_objects(request):
        cases = DrawableObject(request.cases_dict, 'Cases', 'tab:blue')
        deaths = DrawableObject(request.deaths_dict, 'Deaths', 'tab:orange')
        recovered = DrawableObject(request.recovered_dict, 'Recovered', 'seagreen')

        return cases, deaths, recovered

    @staticmethod
    def country_historical(country: CountryHistorical):
        return draw(f"Covid-19 distribution in {country.name}", *Draw.__get_request_drawable_objects(country),
                    filename=country.name.capitalize())

    @staticmethod
    def world_historical(request: WorldHistorical):
        return draw(f"Covid-19 distribution in World", *Draw.__get_request_drawable_objects(request), filename='All')


class DrawableObject:
    def __init__(self, data, name, color):
        self.data = data
        self.name = name
        self.color = color

    def __hash__(self):
        return self.data.__hash__()

    def __gt__(self, other):
        if len(self.data) and len(other.data):
            return list(self.data.values())[-1] > list(other.data.values())[-1]
        return len(self.data) > len(other.data)


def build_pretty_labels(xlabels, max_value, ylabels_cnt=10):
    size = len(xlabels)

    xlabels_indices = []
    xlabels_show_step = len(xlabels) // 20 + 1 if len(xlabels) > 15 else 1

    for i in range(size):
        if i % xlabels_show_step == 0:
            xlabels_indices.append(i)

    xlabels_indices = xlabels_indices[:-1] + [size - 1]

    xlabels_res = [str(xlabels[i]) if i in xlabels_indices else '' for i in range(size)]
    ylabels_res = [0] + [max_value * (i + 1) // ylabels_cnt for i in range(ylabels_cnt)]

    return xlabels_res, ylabels_res


def draw_many_plots(title, xlabels, ylabels, *drawables, filename=None):
    def preprocess_for_plots():
        def self_esteem():
            combined_plots = [0] * len(xlabels)

            for i in range(len(plots)):
                left = len(xlabels) - len(plots[i])
                plots[i] = [0] * left + plots[i]

                if i < len(plot_names) - 1:
                    for j in range(len(plots[i])):
                        combined_plots[j] += plots[i][j]
                else:
                    for q in range(len(plots[i])):
                        plots[i][q] -= combined_plots[q]

        self_esteem()

    fig, ax = plt.subplots()

    drawables = list(reversed([*drawables]))

    plots = [list(d.data.values()) for d in drawables]
    plot_names = [d.name for d in drawables]

    ticks = [i for i in range(len(xlabels))]
    colors = [i.color for i in drawables]

    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel('Cases')

    plt.xticks(ticks, labels=xlabels)
    plt.yticks(ticks=ylabels)

    preprocess_for_plots()

    plt.stackplot(ticks, *plots, labels=plot_names, colors=colors)
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=40, ha="right", rotation_mode="anchor")
    fig.tight_layout()

    plt.legend(loc='upper left')

    if not os.path.exists(STATIC_PATH):
        os.mkdir(STATIC_PATH)

    file_id = filename if filename else plot_names[0]
    time_suffix = datetime.datetime.today().strftime("%Y_%m_%d_%H:%M:%S")

    filename = f'{file_id}_{time_suffix}.png'
    path = os.path.join(STATIC_PATH, filename)

    plt.savefig(path)
    plt.close(fig)

    return path


def draw(title, *drawables, filename=None):
    new = list(drawables)
    for d in drawables:
        if d.data == {}:
            new.remove(d)

    if not new:
        return None

    drawables = sorted(new, reverse=True)
    dicts = [d.data for d in drawables]

    max_value = 0
    xlabels_raw = drawables[0].data.copy()

    for d in dicts:
        xlabels_raw.update(d)
        max_value = max(max_value, max(list(d.values())))

    int_xlabels = list(xlabels_raw.keys())
    xlabels, ylabels = build_pretty_labels(int_xlabels, max_value)

    return draw_many_plots(title, xlabels, ylabels, *drawables, filename=filename)
