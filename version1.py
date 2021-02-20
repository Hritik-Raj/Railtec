import numpy as np
from nptdms import TdmsFile as td
import pandas as pd
import datetime
import scipy
import matlab.engine
import shutil
import os
import glob

os.chdir(r'/Users/hritikraj/Desktop/Railtec')
reqFiletdms = glob.glob('*.tdms')
tdms_file = td.read('/Users/hritikraj/Desktop/Railtec/' + reqFiletdms[0])
num_groups = len(tdms_file.groups())
group = tdms_file['FTA_CTA_Train']

print(group["Sys2"].read_data(scaled=True))
# for item in group:
#     print(group[item].read_data(scaled=True))         // need this part

time = tdms_file['FTA_CTA_Train']["TriggerSys1"].properties["wf_start_time"]
t = time.astype(datetime.datetime)

# if num_groups == 1:
#     f = open('/Users/hritikraj/Desktop/Railtec/FTA_CTA' + t.strftime("%Y%m%d%H%M%S") + '.txt', 'a+')
#     i = 0
#     for item in group:
#         i += 1
#         if i < 2:
#             f.write(str(group[item]) + '\n')
#             f.write(str(group[item].read_data(scaled=True)) + '\n')
#     f.close()

# f = open('/Users/hritikraj/Desktop/Railtec/FTA_CTA' + t.strftime("%Y%m%d%H%M%S") + '.txt', 'a+')
# x = (group["Sys2"].read_data(scaled=True))
# for i in range (0, len(group["Sys2"].read_data(scaled=True))):
#     print(str(x[i]) + '\n')
        
df = group.as_dataframe(time_index = False, absolute_time = True, scaled_data = False)

with open('/Users/hritikraj/Desktop/Railtec/FTA_CTA' + t.strftime("%Y%m%d%H%M%S") + '.txt', 'a+') as f:
    f.write(
        df.to_string(header = True, index = False)
    )

# excel = group.as_dataframe(time_index = False, absolute_time = True, scaled_data = False)

# if num_groups == 1:
#     start_date_time = time
#     location = r'/Users/hritikraj/Desktop/Railtec/FTA_CTA' + t.strftime("%Y%m%d%H%M%S") + '.txt'
#     excel.to_csv(location, index = False, sep='\t', mode = 'a')   // dont know if I need this part




# After finishing TDMS to TXT conversion

source = '/Users/hritikraj/Desktop/Railtec'
reqFiletxt = glob.glob('*tdms')
destination = '/Users/hritikraj/Desktop/Railtec/ProcessedTDMSFiles'

for f in reqFiletxt:
    sourceFile = os.path.join(source, f)
    print( "Moving " + sourceFile + " to " + destination  )
    shutil.move(sourceFile, destination)


eng = matlab.engine.start_matlab()
eng.cd(r'/Users/hritikraj/Desktop/Railtec', nargout=0)
eng.ls(nargout=0)
eng.ProcessingCodeV3(nargout=0)

# Move text files to processed text folder

source = '/Users/hritikraj/Desktop/Railtec'
reqFiletxt = glob.glob('*txt')
destination = '/Users/hritikraj/Desktop/Railtec/ProcessedTextFiles'

for f in reqFiletxt:
    sourceFile = os.path.join(source, f)
    print( "Moving " + sourceFile + " to " + destination  )
    shutil.move(sourceFile, destination)

# Send automated email






