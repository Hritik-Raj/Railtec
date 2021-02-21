import numpy as np
from nptdms import TdmsFile as td
import pandas as pd
import datetime
import scipy
import matlab.engine
import shutil
import os
import glob
import smtplib, ssl

os.chdir(r'/Users/hritikraj/Desktop/Railtec')
reqFiletdms = glob.glob('*.tdms')
tdms_file = td.read('/Users/hritikraj/Desktop/Railtec/' + reqFiletdms[0])
num_groups = len(tdms_file.groups())
group = tdms_file['FTA_CTA_Train']

# print(group["Sys2"].read_data(scaled=True))
# for item in group:
#     print(group[item].read_data(scaled=True))         // need this part

time = tdms_file['FTA_CTA_Train']["TriggerSys1"].properties["wf_start_time"]
t = time.astype(datetime.datetime)

        
# df = group.as_dataframe(time_index = False, absolute_time = True, scaled_data = False)

# with open('/Users/hritikraj/Desktop/Railtec/FTA_CTA' + t.strftime("%Y%m%d%H%M%S") + '.txt', 'a+') as f:
#     f.write(
#         df.to_string(header = True, index = False)
#     )


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

port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "testytesty12321@gmail.com"  # Enter your address
receiver_email = "hritik99@gmail.com"  # Enter receiver address
password = "Skyrimrox1234"
message = """\
Subject: Hi there

This message is sent from Python."""

context = ssl.create_default_context()
with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)




