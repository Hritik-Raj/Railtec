import numpy as np
from nptdms import TdmsFile as td
import pandas as pd
import datetime
tdms_file = td.read('/Users/hritikraj/Desktop/Railtec/FTA_CTA_Trains_37052.tdms')
num_groups = len(tdms_file.groups())
group = tdms_file['FTA_CTA_Train']
for item in group:
    print(group[item].read_data(scaled=True))


# excel = group.as_dataframe(time_index = False, absolute_time = True, scaled_data = False)
# time = tdms_file['FTA_CTA_Train']["TriggerSys1"].properties["wf_start_time"]
# t = time.astype(datetime.datetime)
# if num_groups == 1:
#     start_date_time = time
#     location = r'/Users/hritikraj/Desktop/Railtec/FTA_CTA' + t.strftime("%Y%m%d%H%M%S") + '.txt'
#     excel.to_csv(location, index = False, sep='\t', mode = 'a')





