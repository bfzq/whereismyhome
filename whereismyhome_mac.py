#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
# from pyvirtualdisplay import Display
from selenium import webdriver
import csv,codecs
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

log_root = "./"
# log_root = "C:\\Users\\mtrpc\\iCloudDrive\\Documents\\Projects\\house\\log_root\\"
def isElementExist(driver,element):
    flag=True
    try:
        driver.findElement(element)
        return flag
    except:
        flag=False
        return flag

def writeData(lsts, city):
    date = str(datetime.datetime.now().year) + '_' + str(datetime.datetime.now().month) + '_' + str(datetime.datetime.now().day) + '_' + str(datetime.datetime.now().hour) + '_' + str(datetime.datetime.now().minute)
    filename = city + "'s" + "_" + "houses_price_" + date + ".csv"
    path = log_root + filename
    csv_head = []
    csv_head.append("楼盘")
    csv_head.append("类型")
    csv_head.append("状态")
    csv_head.append("面积")
    csv_head.append("平均价格")
    csv_head.append("单位")
    csv_head.append("平均每套价格")
    csv_head.append("地址")
    csv_head.append("链接")
    with codecs.open(path, 'w', 'utf_8_sig') as f:
        csv_write = csv.writer(f)
        csv_write.writerow(csv_head)
        for item in lsts:
            csv_write.writerow(item)
        f.close()
    return filename

def getDataFrom(driver, page, path):
    path = path + page +"/"
    print("Get Data from path: " + path)
    driver.get(path)
    parent = driver.find_element_by_css_selector("[class='resblock-list-wrapper']")
    sections = parent.find_elements_by_css_selector("[class='resblock-desc-wrapper']")
    lsts = []
    for s in sections:
        name_element = s.find_element_by_class_name("name ")
        name = name_element.text
        link = name_element.get_attribute('href')
        type = s.find_element_by_class_name("resblock-type").text
        status = s.find_element_by_class_name("sale-status").text
        area = s.find_element_by_class_name("resblock-area").text
        address_element = s.find_element_by_class_name("resblock-location")
        address = address_element.find_element_by_tag_name('a').text

        price = s.find_element_by_class_name("resblock-price")
        average_price = price.find_element_by_class_name("number").text
        price_unit = ""
        try:
            price_unit = price.find_element_by_class_name("desc").text
        except:
            price_unit = "unknown"
        total_price = ""
        try:
            total_price = price.find_element_by_class_name("second").text
        except:
            total_price = "not found"
        lst = [name, type, status, area, average_price, price_unit, total_price, address, link]
        lsts.append(lst)
    return lsts

def house_num(driver, path):
    driver.get(path)
    num = driver.find_element_by_class_name("resblock-have-find")
    return num.find_element_by_class_name("value").text

def citys():
    return {"nanchang":"https://nc.fang.lianjia.com/loupan/","shanghai":"https://sh.fang.lianjia.com/loupan/xuhui-huangpu-changning-putuo-pudong-baoshan-hongkou-yangpu-minhang-jiading-songjiang-qingpu-fengxian-jinshan-chongming/"}

def query_houses_price(driver, city):
    path = city[1]
    house_count = int(house_num(driver, path))
    lsts = []
    page_index = 1
    while len(lsts) < house_count:
        page = "pg" + str(page_index)
        lsts += getDataFrom(driver, page, path)
        page_index += 1;
    return writeData(lsts, city[0])

def build_att(file):
    # 构造附件1，传送当前目录下的 test.txt 文件
    path = log_root + file
    att1 = MIMEText(open(path, 'rb').read(), 'base64', 'utf-8')
    att1["Content-Type"] = 'application/octet-stream'
    # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
    att1["Content-Disposition"] = "attachment; filename="+ file
    return att1

def sendemail(file_lst):
    mail_host="smtp.163.com"  #设置服务器
    mail_user="housesprice@163.com"    #用户名
    mail_pass="1qaz2wsx"   #口令
    sender = mail_user
    receivers = ["bigbuggiggle@hotmail.com","609336866@qq.com"]
    message = MIMEMultipart()
    message.attach(MIMEText('Dear 猪摇,\n\n附件为最新的房价表，请查收！\n\n祝每天开心快乐幸福！', 'plain', 'utf-8'))
    message['From'] = "{}".format(sender)
    message['To'] =  ",".join(receivers)
    subject = '南昌，上海新房价格表'
    message['Subject'] = Header(subject, 'utf-8')
    for file in file_lst:
        message.attach(build_att(file))

    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, 465)    # 25 为 SMTP 端口号
        smtpObj.login(mail_user,mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        print ("email send success")
    except smtplib.SMTPException as reason:
        print ("Error: can not send email" + str(reason))

if __name__ == '__main__':
    # display = Display(visible=0, size=(800, 800))
    # display.start()
    option = webdriver.ChromeOptions()
    option.add_argument("headless")
    option.add_argument("start-maximized")
    option.add_argument("disable-infobars")
    option.add_argument("--disable-extensions")
    option.add_argument("--disable-gpu")
    option.add_argument("--disable-dev-shm-usage")
    option.add_argument("--no-sandbox");
    driver = webdriver.Chrome(chrome_options=option)
    citys_ = citys()
    file_lst = []
    for city in citys_.items():
        file_lst.append(query_houses_price(driver, city))

    sendemail(file_lst)
    driver.close()
    driver.quit()
