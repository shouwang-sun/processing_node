# -*- coding: utf-8 -*-
__author__ = 'SUN Shouwang'

import pandas as pd
from streamparse import Stream
from streamparse.bolt import Bolt


class DetrendBolt(Bolt):
    # todo: try pyecharts
    tup_fields = ('timestamp', 'time_offset', 'time_increment', 'samples', 'channel_name', 'module_name', 'data')
    outputs = [Stream(fields=tup_fields, name='detrend')]

    def initialize(self, storm_conf, context):
        # String, dt1: how often to recalculate a mode value, eg. '5s', '20ms'
        # String, dt2: how long data is taken in calculating the mode value, eg. '5s', '20ms'
        self.dt1 = pd.Timedelta(storm_conf.get('dt1', '5s'))
        self.dt2 = pd.Timedelta(storm_conf.get('dt1', '15s'))

    def process(self, tup):
        """
        step 1: accept tup and convert to pandas.Dataframe;
        step 2: call self._detrend() function to remove the mode value from the original data;
        stip 3: convert resulted pandas.Dataframe to list and return.
        :param streamparse.Tuple, tup: tup.values =
                [timestamp, time_offset, time_increment, samples, channel_name, module_name, data]
        :return streamparse.Tuple, tup: tup.values =
                [timestamp, time_offset, time_increment, samples, channel_name, module_name, data]
        """
        timestamp = tup.values[0]
        time_increment = tup.values[2]
        channel_name = tup.values[4]
        data = tup.values[6]

        index = pd.date_range(
            start=pd.Timestamp(timestamp, unit='s', tz='UTC'),
            periods=data.__len__(),
            freq='{}ms'.format(int(time_increment / 0.001))
        )
        df = pd.DataFrame(data=data, index=index, columns=[channel_name])

        try:
            self.history = self.history.combine_first(df)
        except AttributeError:
            self.history = df
            self.freq = df.index.freq
            self.res = list(tup.values)
        self.history = self.history.asfreq(self.freq)

        for df in self._detrend():
            self.res[0] = df.index[0].timestamp()
            self.res[6] = df[channel_name].values.tolist()
            self.emit(self.res, stream='detrend')

    def _detrend(self):
        """
        remove the mode value from the original data
        :return pandas.Dataframe df: de-trended signal segments
        """
        self.log('length of history data: {}'.format(self.history.__len__()), level='info')

        n = int(self.dt1 / self.freq)
        m = int(self.dt2 / self.freq)

        while self.history.__len__() >= m and self.history.head(m).notnull().all().all() \
                or self.history.__len__() >= 2 * m and self.history.head(m).notnull().any().all():
            mode = self.history.head(m).mode()
            df = self.history[:n] - mode.loc[0].values
            self.history = self.history[n:]
            yield df
# EOF
