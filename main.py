from neutral_axis import NeutralAxisBolt
from tdms_parse import TdmsSpout

folder = r'./tdms_files'
channel_list = [u'NLHQ-X-03-S08', u'NLHQ-X-03-S09']
tdms_spout = TdmsSpout(folder, channel_list)

config = {'threshold': 5, 'group_freq': '10s', 'height': [[u'NLHQ-X-03-S08', 0.4], [u'NLHQ-X-03-S09', 0.1]]}
neutral_axis_bolt = NeutralAxisBolt(storm_conf=config, context=None)

for tup in tdms_spout.process():
    for res in neutral_axis_bolt.process(tup):
        print res