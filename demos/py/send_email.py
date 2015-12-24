# -*- coding: UTF-8 -*-
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE,formatdate
from email import encoders
import smtplib
from smtplib import SMTP_SSL
import os
import time
import threading
import logging
import logging.config
import sqlite3_crud
import data_element

PATH_LOG_CONF = '/home/your user name/proj2/conf/logger.conf'
logging.config.fileConfig(PATH_LOG_CONF)
logger = logging.getLogger("example02")
 
#server['name'], server['user'], server['passwd']
def send_mail(server, fro, to, subject, text, files=[]): 
    assert type(server) == dict 
    assert type(to) == list
    assert type(files) == list
 
    msg = MIMEMultipart() 
    msg['From'] = fro 
    msg['Subject'] = subject 
    msg['To'] = ";".join(to)
    msg['Date'] = formatdate(localtime=True) 
    msg.attach(MIMEText(text)) 
 
    for file in files: 
        part = MIMEBase('application', 'octet-stream') #'octet-stream': binary data 
        part.set_payload(open(file, 'rb'.read())) 
        encoders.encode_base64(part) 
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file)) 
        msg.attach(part) 
        
    smtp = smtplib.SMTP_SSL(server['name']) 
    #smtp.set_debuglevel(1)
    smtp.ehlo(server['name'])
    smtp.login(server['user'], server['passwd']) 
    smtp.sendmail(fro, to, msg.as_string()) 
    smtp.close()
    
def getUnfilledTeamMembers(data):
    conn = sqlite3_crud.get_conn(sqlite3_crud.DB_FILE_PATH)
    fetch_sql = 'select reserved from team_members_info where id != 0 and id not in  \
                 (select b.reserved from task_info a,daily_cost b where a.task_id = b.task_id and b.cost_day = ?)'
                 #reserved indicates the email of team member, except id = 0 (name = ALL)
    if conn is not None:
        result = sqlite3_crud.fetch(conn, fetch_sql, data)
        if result is not None:
            logger.debug('successfully fetch %d datas who did not commit task burndown info from team members', len(result))
            return result
    else:
        logger.error('get datas who did not commit task burndown info failed:conn to db[%s] is None', sqlite3_crud.DB_FILE_PATH)
    return None
    
def sendEmailTimer():
    yesterday = time.localtime(time.time() - (1 * 24 * 3600))
    weekNo = time.strftime('%w', yesterday)
    if weekNo != '0' and weekNo != '6':
        str_yesterday = time.strftime('%m/%d/%Y', yesterday)
        data = [str_yesterday]
        result = getUnfilledTeamMembers(data)
        if result is not None:
            if len(result) > 0:
                server = {"name" : "smtp.sina.com", "user" : "xxx", "passwd" : "xxx"}
                fro = 'xxx@sina.com'
                email_to = [i[0] for i in result]
                subject = 'Just a kind reminder that please record your task burndown info in kanban!'
                text = 'http://xxx.xxx.xxx.xxx:8080/kanban       Uncommitted date:[' + str_yesterday + ']'
                send_mail(server, fro, email_to, subject, text)
    t = threading.Timer(1 * 24 * 3600, sendEmailTimer)
    t.start()
    
#if __name__ == "__main__":
#    sendEmailTimer()