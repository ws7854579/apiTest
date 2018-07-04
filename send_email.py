# -*- coding:utf-8 -*-
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from logger import Logger
import os

logger = Logger('sendEmail').getlog()

def send_mail(file_report):
    f = open(file_report,'rb')
    mail_body = f.read()
    f.close()
    smtpserver = 'smtp.qq.com'
    sender = '790708124@qq.com'
    receiver = 'sunsuwei@ccx.cn'
    mail_user = '790708124@qq.com'
    mail_pass = 'vdxiyoesfibdbdgf'
    msg = MIMEMultipart()
    text = MIMEText(mail_body,'html','utf-8')
    text['Subject'] = Header('测试报告','utf-8')
    msg.attach(text)
    msg_file = MIMEText(mail_body,'html','utf-8')
    msg['Subject'] = Header('测试报告ttt','utf-8')
    msg_file['Content-Type'] = 'application/octet-stream'
    msg_file['Content-Disposition'] = 'attachment; filename="TestReport.html"'
    msg.attach(msg_file)
    msg['from'] = '790708124@qq.com'
    msg['to'] = 'sunsuwei@ccx.cn'
    try:
        smtp = smtplib.SMTP_SSL('smtp.qq.com',465)
        smtp.login(mail_user,mail_pass)
        smtp.sendmail(msg['from'],msg['to'],msg.as_string())
        smtp.quit()
        logger.info('Send email successful!')
    except smtplib.SMTPException,e:
        logger.info('Failed,%s'%e)

def new_report(report_path):
    dirs = os.listdir(report_path)
    dirs.sort(reverse=True)
    newreportname = dirs[0]
    logger.info('The new report name:%s'%newreportname)
    file_new = os.path.join(report_path,newreportname)
    logger.info('The return name is:%s'%file_new)
    return file_new
