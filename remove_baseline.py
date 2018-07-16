# -*- coding: utf-8 -*-
__author__ = 'SUN Shouwang'

import pandas as pd


def detrend(data, freq, lag=None):
    """
    define the modal (most frequent) value as the baseline of input signal,
    and subtract the baseline from input signal
    :param pandas.DataFrame, data: original data
    :param pandas.Timedelta, freq: how often to recalculate a mode value
    :param pandas.Timedelta, lag: time lag before a mode value is calculated
    :return pandas.DataFrame, data: detrended data
    :return pandas.DataFrame, mode: the modal value of the original data
    """
    if not lag:
        lag = 3 * freq

    try:
        detrend.history = detrend.history.combine_first(data)
    except AttributeError:
        detrend.history = data
        detrend.freq = data.index.freq

    detrend.history = detrend.history.asfreq(detrend.freq)
    print(detrend.history.__len__())

    n = int(freq / detrend.freq)
    m = int(lag / detrend.freq)

    if detrend.history.__len__() >= 2 * m \
            or detrend.history.__len__() >= m \
            and detrend.history.head(m).notnull().all().all():
        mode = detrend.history.head(m).mode()
        mode = mode[:1].rename(index={0: detrend.history.index[0]})
        data = detrend.history[:n] - mode.iloc[0]
        detrend.history = detrend.history[n:]
    try:
        return data, mode
    except UnboundLocalError:
        pass


if __name__ == '__main__':
    from os import path, listdir
    from read_tdms_file import read_tdms_file

    directory = 'tdms_files'
    channel_list = [u'NLHQ-X-03-S08', u'NLHQ-X-03-S09']
    file_list = [path.join(directory, listdir(directory)[i]) for i in range(10) if i != 2]
    for file_name in file_list:
        df = read_tdms_file(file_name, channel_list)
        ret = detrend(df, pd.Timedelta('5s'))
        if ret:
            data, mode = ret
            print data.head()
            print mode
