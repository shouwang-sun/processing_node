# -*- coding: utf-8 -*-
__author__ = 'SUN Shouwang'

import pandas as pd
from numpy import polyfit
from streamparse import Stream
from streamparse.bolt import Bolt


# noinspection PyAttributeOutsideInit
class NeutralAxisBolt(Bolt):
    tup_fields = ('timestamp_min', 'timestamp_max', 'neutral_axis')
    outputs = [Stream(fields=tup_fields, name='neutral_axis')]

    def initialize(self, storm_conf, context):
        """
        receive parameters set in topology definition from storm_conf argument
        :param dict storm_conf: the Storm configuration for this component
        :param dict context: information about the component’s place within the topology
        """

        threshold = storm_conf['threshold']
        group_freq = storm_conf['group_freq']
        height = storm_conf['height']

        height = dict(height)
        columns = height.keys()
        index = pd.MultiIndex.from_tuples([], names=['group_time', 'sample_time'])

        self.threshold = threshold
        self.group_freq = group_freq
        self.height = pd.Series(height, name='height')
        self.height.sort_values(ascending=True, inplace=True)
        self.history = pd.DataFrame(data=[], index=index, columns=columns)

    def process(self, tup):
        """
        step 1: receive tup and reorganize to pandas.Dataframe;
        step 2: call self._neutral_axis() function to get the neutral axis height of a section ;
        step 3: convert resulted pandas.Dataframe to list and send out.
        :param streamparse.Tuple, tup: tup.values =
                [timestamp, time_offset, time_increment, samples, channel_name, module_name, data]
        :return streamparse.Tuple, tup: tup.values =
                [minima_timestamp, maxima_timestamp, neutral_axis]
        """
        # convert tuple to pandas.DataFrame with pandas.MultiIndex
        timestamp = tup.values[0]
        time_increment = tup.values[2]
        channel_name = tup.values[4]
        data = tup.values[6]

        start = pd.Timestamp(timestamp, unit='s', tz='UTC')
        periods = data.__len__()
        freq = '{}ms'.format(int(time_increment / 0.001))

        sample_time = pd.date_range(start=start, periods=periods, freq=freq)
        group_time = sample_time.floor(self.group_freq)

        index = pd.MultiIndex.from_arrays([group_time, sample_time], names=['group_time', 'sample_time'])
        df = pd.DataFrame(data=data, index=index, columns=[channel_name])

        # self.history holds all history data
        self.history = self.history.combine_first(df)
        # todo: discard history data 10 minutes before the latest data

        # group self.history by index <group_time> level
        notnull_count = self.history.groupby(level='group_time').apply(lambda x: x.notnull().sum().sum())
        count = self.history.columns.size * pd.Timedelta(self.group_freq) / pd.Timedelta(freq)
        notnull_count = notnull_count[notnull_count >= count]

        if not notnull_count.empty:
            # extract data ready for processing and discard them from history data
            data_ready = self.history.loc[notnull_count.index]
            self.history.drop(index=notnull_count.index, level='group_time', inplace=True)

            res = data_ready.groupby(level='group_time').apply(self._neutral_axis)
            for idx in res.index:
                self.emit(res[idx], stream='neutral_axis')

    def _neutral_axis(self, df):
        self.log('---------------excuting neutral_axis method---------------')
        master_channel = self.height.index[0]

        if df[master_channel].ptp() > self.threshold:
            idx_max = df[master_channel].idxmax()
            idx_min = df[master_channel].idxmin()
            ptp = df.loc[idx_max] - df.loc[idx_min]
            ptp.rename('ptp', inplace=True)

            xy = pd.concat([ptp, self.height], axis='columns')
            # deg = 1 stands for linear fit
            # the lowest polynomial coefficients (y-intercept) is the height of neutral axis
            neutral_axis = polyfit(xy['ptp'], xy['height'], 1)[-1]

            return [idx_min[1].timestamp(), idx_max[1].timestamp(), neutral_axis]
