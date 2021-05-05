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
from email import encoders
import time 
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase


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
    currentFile = ""
    for f in reqFiletxt:
        currentFile = f
        sourceFile = os.path.join(source, f)
        print( "Moving " + sourceFile + " to " + destination)
        shutil.move(sourceFile, destination)
    return currentFile

def moveCSV(source, destination):
    reqFiletxt = glob.glob('*csv')
    for f in reqFiletxt:
        sourceFile = os.path.join(source, f)
        print( "Moving " + sourceFile + " to " + destination)
        shutil.move(sourceFile, destination)

def mime_init(from_addr, recipients_addr, subject, body):
    """
    :param str from_addr:           The email address you want to send mail from
    :param list recipients_addr:    The list of email addresses of recipients
    :param str subject:             Mail subject
    :param str body:                Mail body
    :return:                        MIMEMultipart object
    """

    msg = MIMEMultipart()

    msg['From'] = from_addr
    msg['To'] = ','.join(recipients_addr)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    return msg

def sendEmail(from_addr, password, recipients_addr, subject, body, files_path=None, server='smtp.gmail.com'):
    """
    :param str user:                Sender's email userID
    :param str password:            sender's email password
    :param str from_addr:           The email address you want to send mail from
    :param list recipients_addr:    List of (or space separated string) email addresses of recipients
    :param str subject:             Mail subject
    :param str body:                Mail body
    :param list files_path:         List of paths of files you want to attach
    :param str server:              SMTP server (port is choosen 587)
    :return:                        None
    """

    #   assert isinstance(recipents_addr, list)
    FROM = from_addr
    TO = recipients_addr if isinstance(recipients_addr, list) else recipients_addr.split(' ')
    PASS = password
    SERVER = server
    SUBJECT = subject
    BODY = body
    msg = mime_init(FROM, TO, SUBJECT, BODY)

    for file_path in files_path or []:
        with open(file_path, "rb") as fp:
            part = MIMEBase('application', "octet-stream")
            part.set_payload((fp).read())
            # Encoding payload is necessary if encoded (compressed) file has to be attached.
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment; filename= %s" % os.path.basename(file_path))
            msg.attach(part)

    if SERVER == 'localhost':   # send mail from local server
        # Start local SMTP server
        server = smtplib.SMTP(SERVER)
        text = msg.as_string()
        server.send_message(msg)
    else:
        # Start SMTP server at port 587
        server = smtplib.SMTP(SERVER, 587)
        server.starttls()
        # Enter login credentials for the email you want to sent mail from
        server.login(from_addr, PASS)
        text = msg.as_string()
        # Send mail
        server.sendmail(FROM, TO, text)

    server.quit()

# Send automated email

# def sendEmail(sender_email, receiver_email, password):
    # port = 465  # For SSL
    # smtp_server = "smtp.gmail.com"
    # message = """\
    # Subject: Hi there

    # Anomaly detected in train."""

    # context = ssl.create_default_context()
    # with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    #     server.login(sender_email, password)
    #     server.sendmail(sender_email, receiver_email, message)



    # dir_path = "G:/test_runners/selenium_regression_test_5_1_1/TestReport"
    # files = ["SeleniumTestReport_part1.html", "SeleniumTestReport_part2.html", "SeleniumTestReport_part3.html"]

    # msg = MIMEMultipart()
    # msg['To'] = "4_server_dev@company.com"
    # msg['From'] = "system@company.com"
    # msg['Subject'] = "Selenium ClearCore_Regression_Test_Report_Result"

    # body = MIMEText('Test results attached.', 'html', 'utf-8')  
    # msg.attach(body)  # add message body (text or html)

    # for f in files:  # add files to the message
    #     file_path = os.path.join(dir_path, f)
    #     attachment = MIMEApplication(open(file_path, "rb").read(), _subtype="txt")
    #     attachment.add_header('Content-Disposition','attachment', filename=f)
    #     msg.attach(attachment)

    # s = smtplib.SMTP()
    # s.connect(host=SMTP_SERVER)
    # s.sendmail(msg['From'], msg['To'], msg.as_string())
    # print 'done!'
    # s.close()
def findFig(source):
    reqFiletxt = glob.glob('*fig')
    retArr = []
    for f in reqFiletxt:
        sourceFile = os.path.join(source, f)
        retArr.append(sourceFile)
    return retArr

def analyzePeaks(V1_peaks, V2_peaks, name):
    body = " To whomsever this may concern, the following anomalies have been detected in the train that passed by the sensor at " + name + "\n"
    for i in range(len(V1_peaks)):
        if V1_peaks[i] >= 12:
            body += "Anomaly " + str(i) +  ":" + str(V1_peaks[i]) + "\n"
        if V2_peaks[i] >= 12:
            body += "Anomaly " + str(i) +  ":" + str(V2_peaks[i]) + "\n"       
    files_path = findFig('/Users/hritikraj/Desktop/Railtec')
    sendEmail("testytesty12321@gmail.com", "Skyrimrox1234", ["hritik99@gmail.com", "shivangi.sharma9536@gmail.com"], "Warning Email", body, files_path)


def scanDF(df, name):
    V1_peaks = df.loc[:, "V1_pks"].values
    V2_peaks = df.loc[:, "V2_pks"].values
    analyzePeaks(V1_peaks, V2_peaks, name)


def processCSV(name):
    filenames = glob.glob('*csv')
    for f in filenames:
        df = pd.read_csv(f)
        scanDF(df, name)

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
        name = moveText('/Users/hritikraj/Desktop/Railtec', '/Users/hritikraj/Desktop/Railtec/ProcessedTextFiles') 
        # processFilterCSV()
        moveFilterCSV('/Users/hritikraj/Desktop/Railtec', '/Users/hritikraj/Dropbox/Apps/RailTEC/TextFiles')  
        processCSV(name)
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

