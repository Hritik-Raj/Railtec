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
import watchdog.events 
import watchdog.observers 
import time 


def tdmsTransform(directory, filePath):
    reqFiletdms = glob.glob('*.tdms')
    tdms_file = td.read(directory + reqFiletdms[0])
    num_groups = len(tdms_file.groups())
    if num_groups == 1:
        group = tdms_file['FTA_CTA_Train']

        time = tdms_file['FTA_CTA_Train']["TriggerSys1"].properties["wf_start_time"]
        t = time.astype(datetime.datetime)
        df = group.as_dataframe(time_index = False, absolute_time = True)
        with open(filePath + t.strftime("%Y%m%d%H%M%S") + '.txt', 'a+') as f:
            f.write(df.to_string(header = True, index = False))
    else:
        return

# print(group["Sys2"].read_data(scaled=True))
# for item in group:
#     print(group[item].read_data(scaled=True))         // need this part


# if num_groups == 1:
#     start_date_time = time
#     location = r'/Users/hritikraj/Desktop/Railtec/FTA_CTA' + t.strftime("%Y%m%d%H%M%S") + '.txt'
#     excel.to_csv(location, index = False, sep='\t', mode = 'a')   // dont know if I need this part



def moveTDMS(source, destination):
    reqFiletxt = glob.glob('*tdms')
    for f in reqFiletxt:
        sourceFile = os.path.join(source, f)
        print( "Moving " + sourceFile + " to " + destination  )
        shutil.move(sourceFile, destination)

def matlabCall(location):
    eng = matlab.engine.start_matlab()
    eng.cd(location, nargout=0)
    eng.ls(nargout=0)
    eng.ProcessingCodeV3(nargout=0)
    testing = eng.workspace['axleInfo']
    print(testing)

# Move text files to processed text folder
def moveText(source, destination):
    reqFiletxt = glob.glob('*txt')
    for f in reqFiletxt:
        sourceFile = os.path.join(source, f)
        print( "Moving " + sourceFile + " to " + destination)
        shutil.move(sourceFile, destination)

def moveCSV(source, destination):
    reqFiletxt = glob.glob('*csv')
    for f in reqFiletxt:
        sourceFile = os.path.join(source, f)
        print( "Moving " + sourceFile + " to " + destination)
        shutil.move(sourceFile, destination)

# Send automated email
def sendEmail(sender_email, receiver_email, password):
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    message = """\
    Subject: Hi there

    Anomaly detected in train."""

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)

def analyzePeaks(V1_peaks, V2_peaks):
    for i in range(len(V1_peaks)):
        if V1_peaks[i] or V2_peaks[i] >= 21:
            sendEmail("testytesty12321@gmail.com", "hritik99@gmail.com", "Skyrimrox1234")


def scanDF(df):
    V1_peaks = df.loc[:, "V1_pks"].values
    V2_peaks = df.loc[:, "V2_pks"].values


def processCSV():
    filenames = glob.glob('*csv')
    for f in filenames:
        df = pd.read_csv(f)
        scanDF(df)

# def processFilterCSV():
#     filenames = glob.glob('*csv')
#     for f in filenames:
#         df = pd.read_csv(f)
#         scanDF(df)

def moveFilterCSV(source, destination):
    reqFiletxt = glob.glob('filter*.csv')
    for f in reqFiletxt:
        sourceFile = os.path.join(source, f)
        print( "Moving " + sourceFile + " to " + destination)
        shutil.move(sourceFile, destination)

# def timelogger():
    

  
  
class Handler(watchdog.events.PatternMatchingEventHandler): 
    def __init__(self): 
        # Set the patterns for PatternMatchingEventHandler 
        watchdog.events.PatternMatchingEventHandler.__init__(self, patterns=['*.tdms'], 
                                                             ignore_directories=True, case_sensitive=False) 
  
    def on_created(self, event): 
        print("Watchdog received created event - % s." % event.src_path) 
        # Event is created, you can process it now 
        tdmsTransform('/Users/hritikraj/Desktop/Railtec/', '/Users/hritikraj/Desktop/Railtec/FTA_CTA')
        #sleep
        moveTDMS('/Users/hritikraj/Desktop/Railtec', '/Users/hritikraj/Desktop/Railtec/ProcessedTDMSFiles')
        #sleep
        matlabCall(r'/Users/hritikraj/Desktop/Railtec')
        #sleep
        moveText('/Users/hritikraj/Desktop/Railtec', '/Users/hritikraj/Desktop/Railtec/ProcessedTextFiles') 
        # processFilterCSV()
        moveFilterCSV('/Users/hritikraj/Desktop/Railtec', '/Users/hritikraj/Dropbox/Apps/RailTEC/TextFiles')  
        processCSV()
        moveCSV('/Users/hritikraj/Desktop/Railtec', '/Users/hritikraj/Dropbox/Apps/RailTEC/TextFiles')
        # sendEmail("testytesty12321@gmail.com", "hritik99@gmail.com", "Skyrimrox1234")

    def on_modified(self, event): 
        print("Watchdog received modified event - % s." % event.src_path) 
        # Event is modified, you can process it now 
  
  
if __name__ == "__main__": 
    src_path = r'/Users/hritikraj/Desktop/Railtec'
    event_handler = Handler() 
    observer = watchdog.observers.Observer() 
    observer.schedule(event_handler, path=src_path, recursive=True) 
    observer.start() 
    try: 
        while True: 
            time.sleep(1) 
    except KeyboardInterrupt: 
        observer.stop() 
    observer.join() 



# need to create new files to store data (TDMS and text files for every week)

