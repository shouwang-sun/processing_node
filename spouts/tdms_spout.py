# -*- coding: utf-8 -*-
__author__ = 'SUN Shouwang'

import time
from os import listdir, path

import nptdms


class TdmsSpout(object):

    def __init__(self, folder, channel_list):
        random_index = [3, 0, 2, 5, 1, 7, 4, 8, 6, 9]
        self.file_list = [path.join(folder, listdir(folder)[ind]) for ind in random_index]
        # self.file_list = [path.join(folder, file_name) for file_name in listdir(folder)][:100]
        self.channel_list = channel_list

    def process(self):
        for tup in self._parse():
            yield tup

    def _parse(self):
        for file_name in self.file_list:
            tdms_file = nptdms.TdmsFile(file_name)
            for channel_name in self.channel_list:
                channel_object = tdms_file.object(u'未命名', channel_name)

                # acquire this channel's 'wf_start_time' property
                # and get its timestamp value for JSON serialize
                start_time = channel_object.property('wf_start_time')
                timestamp = time.mktime(start_time.timetuple())
                tup = [timestamp]

                # acquire this channel's other properties
                others = [v for k, v in channel_object.properties.items() if k != 'wf_start_time']
                tup.extend(others)

                # acquire channel data
                data = channel_object.data.tolist()
                tup.append(data)

                yield tup
