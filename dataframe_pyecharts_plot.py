# -*- coding: utf-8 -*-
__author__ = 'SUN Shouwang'

from pyecharts import Line
from pyecharts.conf import PyEchartsConfig
from pyecharts.engine import EchartsEnvironment
from pyecharts.utils import write_utf8_html_file


def dataframe_line_plot(df, title='', path=None):
    option = {
        'title': {
            'text': title,
            'left': 'center'
        },
        'legend': {
            'show': True,
            'orient': 'vertical',
            'right': '9%',
            'top': '3%'
        },
        'xAxis': {
            'type': 'time',
            'axisLine': {
                'onZero': False
            }
        },
        'yAxis': {
            'axisLine': {
                'onZero': False
            }
        },
        'dataZoom': [
            {
                'type': 'slider',
                'xAxisIndex': 0,
                'start': 0,
                'end': 50
            }
        ]
    }

    time = [ts.timestamp() / 0.001 for ts in df.index]
    series = []
    for channel in df.columns:
        values = df[channel].values.tolist()
        data = [(t, x) for t, x in zip(time, values)]
        series.append(
            {
                'type': 'line',
                'showSymbol': False,
                'name': channel,
                'data': data
            }
        )
    option.update({'series': series})

    line_plot = Line()
    line_plot._option.update(option)

    conf = PyEchartsConfig(
        echarts_template_dir='html',
        jshost='js',
        force_js_embed=False
    )
    env = EchartsEnvironment(pyecharts_config=conf)
    tpl = env.get_template('template.html')
    html = tpl.render(chart=line_plot)
    write_utf8_html_file(path, html)


if __name__ == '__main__':
    from os import listdir, path
    from read_tdms_file import read_tdms_files

    folder = 'tdms_files'
    file_list = [path.join(folder, file_name) for file_name in listdir(folder)][0:50]

    channel_list = [u'NLHQ-X-03-S08', u'NLHQ-X-03-S09']
    raw_data = read_tdms_files(file_list, channel_list)

    dataframe_line_plot(raw_data, title='原始数据', path=r'html\raw_data.html')
