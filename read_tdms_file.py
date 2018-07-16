# -*- coding: utf-8 -*-
__author__ = 'SUN Shouwang'

# version 2.0
import nptdms


def read_tdms_file(file_name, channel_list):
    """
    return as Pandas DataFrame data of channels specified in <channel_list> from <file_name>
    :param file_name: string, the full name of a .tdms file
    :param channel_list: list of strings, list of channel names, must be contained in the tdms file
    :return: pandas DataFrame, each column corresponding to one element of <channel_list>
    """
    tdms_file = nptdms.TdmsFile(file_name)
    df = tdms_file.as_dataframe(time_index=True, absolute_time=True)
    # 重命名列，原列名称</'未命名'/'NLHQ-X-03-S05'>，新列名称<NLHQ-X-03-S05>
    df.rename(columns=lambda name: name.split('/')[-1].strip('\''), inplace=True)

    return df[channel_list]


def read_tdms_files(file_list, channel_list):
    """
    read data of channels specified in <channel_list> from all tdms files in <file_list>
    :param file_list: list of strings, the full name of a sequence of tdms files
    :param channel_list: list of strings, list of channel names, must be contained in all tdms files
    :return: pandas DataFrame, each column corresponding to one element of <channel_list>
    """

    for file_name in file_list:
        try:
            df = df.combine_first(read_tdms_file(file_name, channel_list))
        except UnboundLocalError:
            df = read_tdms_file(file_name, channel_list)

    return df

# version 1.0
# import nptdms
# import numpy as np
# import pandas as pd
#
#
# def read_tdms_file(file_name, group_name, channel_name):
#     """
#     read data from LabVIEW TDMS files
#     :param file_name, string
#     :param group_name, string
#     :param channel_name, string
#     :return: pandas series
#     """
#
#     tdms_file = nptdms.TdmsFile(file_name)
#     channel = tdms_file.object(group_name, channel_name)
#
#     data = channel.data
#     time = channel.time_track(absolute_time=True, accuracy='ms')
#
#     return pd.Series(data=data, index=time, name=channel_name)
#
#
# def read_tdms_files(file_list, group_name, channel_list):
#     dataframe = pd.DataFrame()
#     for file_name in file_list:
#         for channel_name in channel_list:
#             series = read_tdms_file(file_name, group_name, channel_name)
#             dataframe = dataframe.combine_first(pd.DataFrame(series))
#     return dataframe
