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
from dotenv import load_dotenv
import boto3
from botocore.exceptions import NoCredentialsError
import psycopg2
from google.transit import gtfs_realtime_pb2
import requests
import json
from geopy import distance



# function to detect train within geo fence everytime an event is logged in local folder. Makes API call in a loop

def gtfsAPI():
    feed = gtfs_realtime_pb2.FeedMessage()
    response = requests.get('https://gtfsapi.metrarail.com/gtfs/positions', auth=(GTFSAccess, GTFSPassword), allow_redirects = True)
    arrayCoord = []
    jsonValue = response.json()
    for item in jsonValue:
        arrayCoord.append(tuple(item['vehicle']['position']['latitude'], item['vehicle']['position']['longitude']))
    
    retval = trainNumber(arrayCoord)
    if retval == -1:
        return tuple(-1, -1, -1)
    else:
        trainId = jsonValue[retval]['id']
        tripId = jsonValue[retval]['vehicle']['trip']['trip_id']
        routeId = jsonValue[retval]['vehicle']['trip']['route_id']
        return tuple(trainId, tripId, routeId)

def trainNumber(arrayCoord):
    center_point = [{'lat': -7.7940023, 'lng': 110.3656535}]
    radius = 0.46 # in kilometer

    center_point_tuple = tuple(center_point[0].values()) # (-7.7940023, 110.3656535)
    for i, item in enumerate(arrayCoord):
        dis = distance.distance(center_point_tuple, item).km
        print("Distance: {}".format(dis)) # Distance: 0.0628380925748918

        if dis <= radius:
            return i
    return -1



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


# def uploadCSV(source, bucket_normal, s3_name, ACCESS_KEY, SECRET_KEY):
#     reqFiletxt = glob.glob('*csv')
#     s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
#                       aws_secret_access_key=SECRET_KEY)
#     for fileName in reqFiletxt:
#         sourceFile = os.path.join(source, fileName)
#         # print( "Moving " + sourceFile + " to " + destination)
#         # shutil.move(sourceFile, destination)
#         try:
#             s3.upload_file(sourceFile, bucket_normal, fileName)
#             print("Upload Successful")
#             return True
#         except FileNotFoundError:
#             print("The file was not found")
#             return False
#         except NoCredentialsError:
#             print("Credentials not available")
#             return False


# def uploadCSVfilter(source,  bucket_filter, s3_name, ACCESS_KEY, SECRET_KEY):
#     s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
#                       aws_secret_access_key=SECRET_KEY)
#     reqFilefilter = glob.glob('filter*.csv')
#     for fileName in reqFilefilter:
#         sourceFile = os.path.join(source, fileName)
#         try:
#             s3.upload_file(sourceFile, bucket_filter, fileName)
#             print("Upload Filter Successful")
#             return True
#         except FileNotFoundError:
#             print("The file was not found")
#             return False
#         except NoCredentialsError:
#             print("Credentials not available")
#             return False




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

def findFig(source):
    reqFiletxt = glob.glob('*fig')
    retArr = []
    for f in reqFiletxt:
        sourceFile = os.path.join(source, f)
        retArr.append(sourceFile)
    return retArr

def analyzePeaks(V1_peaks, V2_peaks, name, trainDetails):
    if trainDetails[0] != -1 and trainDetails[1] != -1 and trainDetails[2] != -1:
        body = " To whomsever this may concern, the following anomalies have been detected in Train ID :" + str(trainDetails[0]) + "\n" + "Trip ID :" + str(trainDetails[1]) + "\n" + "Route ID :" + str(trainDetails[2]) + "\n" + " which passed by the sensor at " + name + "\n"
    else:
        body = " To whomsever this may concern, the following anomalies have been detected in the train that passed by the sensor at " + name + "\n"
    for i in range(len(V1_peaks)):
        if V1_peaks[i] >= 12:
            body += "Anomaly " + str(i) +  ":" + str(V1_peaks[i]) + "\n"
        if V2_peaks[i] >= 12:
            body += "Anomaly " + str(i) +  ":" + str(V2_peaks[i]) + "\n"       
    files_path = findFig('/Users/hritikraj/Desktop/Railtec')
    sendEmail("testytesty12321@gmail.com", "Skyrimrox1234", ["hritik99@gmail.com", "shivangi.sharma9536@gmail.com"], "Warning Email", body, files_path)


def scanDF(df, name, trainDetails):
    V1_peaks = df.loc[:, "V1_pks"].values
    V2_peaks = df.loc[:, "V2_pks"].values
    analyzePeaks(V1_peaks, V2_peaks, name, trainDetails)


def processCSV(name, trainDetails):
    filenames = glob.glob('*csv')
    for f in filenames:
        df = pd.read_csv(f)
        scanDF(df, name, trainDetails)

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

def moveCSV(source, destination):
    reqFiletxt = glob.glob('*csv')
    for f in reqFiletxt:
        sourceFile = os.path.join(source, f)
        print( "Moving " + sourceFile + " to " + destination)
        shutil.move(sourceFile, destination)
    
def createTable(tableName):
    cursor.execute("CREATE TABLE " + tableName + """(
    trainNumber integer,
    trainDate text,
    trainSpeed float,
    trainAxle integer,
    V1_pks float,
    V2_pks float,
    L1_pks float,
    L2_pks float)""")

def createFilterTable(tableName):
    cursor.execute("CREATE TABLE " + tableName + """(
    a float,
    b float,
    c float,
    d float,
    e float,
    f float,
    g float,
    h float)""")


def uploadFilterCSV(source):
    reqFilefilter = glob.glob('filter*.csv')
    for fileName in reqFilefilter:
        sourceFile = os.path.join(source, fileName)
        createFilterTable(fileName[:len(fileName) - 4])
        with open(sourceFile, 'r') as row:
            cursor.copy_from(row, fileName[:len(fileName) - 4], sep=',')


        
def uploadCSV(source):
    reqFile = glob.glob('*.csv')
    for fileName in reqFile:
        sourceFile = os.path.join(source, fileName)
        createTable('raw' + fileName[:len(fileName) - 4])
        with open(sourceFile, 'r') as row:
            next(row)
            cursor.copy_from(row, 'raw' + fileName[:len(fileName) - 4], sep=',', null='')
        connection.commit()

    
  
class Handler(watchdog.events.PatternMatchingEventHandler): 
    def __init__(self): 
        # Set the patterns for PatternMatchingEventHandler 
        watchdog.events.PatternMatchingEventHandler.__init__(self, patterns=['*.tdms'], 
                                                             ignore_directories=True, case_sensitive=False) 
  
    def on_created(self, event): 
        print("Watchdog received created event - % s." % event.src_path) 
        trainDetails = gtfsAPI()
        # Event is created, you can process it now 
        tdmsTransform('/Users/hritikraj/Desktop/Railtec/', '/Users/hritikraj/Desktop/Railtec/FTA_CTA')
        moveTDMS('/Users/hritikraj/Desktop/Railtec', '/Users/hritikraj/Desktop/Railtec/ProcessedTDMSFiles')
        matlabCall(r'/Users/hritikraj/Desktop/Railtec')
        name = moveText('/Users/hritikraj/Desktop/Railtec', '/Users/hritikraj/Desktop/Railtec/ProcessedTextFiles') 
          
        # uploadedCSVfiler = uploadCSVfilter('/Users/hritikraj/Desktop/Railtec', 'railcsvfilter', '', AWS_ID, AWS_PWD)
        
        # if uploadedCSVfiler:
        #     print("Filtered data successfully uploaded to AWS")

        uploadFilterCSV('/Users/hritikraj/Desktop/Railtec')
        moveFilterCSV('/Users/hritikraj/Desktop/Railtec', '/Users/hritikraj/Desktop/Railtec/ProcessedCSVfilter')
        processCSV(name, trainDetails)
        uploadCSV('/Users/hritikraj/Desktop/Railtec')
        moveCSV('/Users/hritikraj/Desktop/Railtec', '/Users/hritikraj/Desktop/Railtec/ProcessedCSV')



        # uploadedCSV = uploadCSV('/Users/hritikraj/Desktop/Railtec', 'railcsv', '', AWS_ID, AWS_PWD)
        
        # if uploadedCSV:
        #     print("Upload to AWS successful")

    def on_modified(self, event): 
        print("Watchdog received modified event - % s." % event.src_path) 
        # Event is modified, you can process it now 




if __name__ == "__main__": 
    src_path = r'/Users/hritikraj/Desktop/Railtec'
    load_dotenv()
    AWS_ID = os.getenv('AWSAccessKeyId')
    AWS_PWD = os.getenv('AWSSecretKey')
    GTFSAccess = os.getenv('GTFSAccessKey')
    GTFSPassword = os.getenv('GTFSSecretKey')


    connection = psycopg2.connect(
    host = os.getenv('AWSDBEndpoint'),
    port = 5432,
    user = os.getenv('AWSUserName'),
    password = os.getenv('AWSDBPassword'),
    database=os.getenv('AWSDatabaseName')
    )
    cursor=connection.cursor()

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

