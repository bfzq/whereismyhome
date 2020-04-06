#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
# from pyvirtualdisplay import Display
from selenium import webdriver
# import csv,codecs
import datetime
import smtplib
import mysql_tool as my
import time

def get_date():
    return time.strftime("%Y-%m-%d", time.localtime())

def isElementExist(driver,element):
    flag=True
    try:
        driver.findElement(element)
        return flag
    except:
        flag=False
        return flag

def find_housing_estate_id(cnx, housing_estate_name, housing_estate_city,
                           housing_estate_type):
    sql = "SELECT ID FROM HOUSING_ESTATE WHERE NAME = '{}' AND city = '{}' AND TYPE = '{}'".format(housing_estate_name, housing_estate_city, housing_estate_type)
    id_ = my.query(cnx, sql)
    count = len(id_)
    if count > 1:
        print("Query more than 1({}) id from housing_estate.".format(id_.count()))
        exit(1)
    elif count == 1:
        return id_[0][0]
    else:
        return -1

def cut_area_string(area):
    if area.strip() == '':
        return ("0","0")
    area = area[3:-1]
    idx = area.find('-')
    if idx == -1:
        return (area, area)
    else:
        return (area[:idx],area[idx + 1:])

# 检查当天小区的价格是否记录
def housing_estate_record_exists_for_date(cnx, housing_estate_id, date):
    sql = "SELECT 1 FROM HOUSING_ESTATE_PRICE WHERE HOUSING_ESTATE_ID = {} AND DATE = '{}'".format(housing_estate_id, date)
    exists = my.query(cnx, sql)
    if len(exists) == 0:
        return False
    else:
        return True

def store_housing_estate_price(cnx, name, city, type_, status, area,
                               average_price, price_unit, address, link, date_):
    id_ = find_housing_estate_id(cnx, name, city, type_)
    if id_ == -1:
        area_pair = cut_area_string(area)
        sql1 = "INSERT INTO `HOUSING_ESTATE`(`NAME`, `CITY`, `TYPE`, `IS_SECOND_HAND`,`AREA_MIN`, `AREA_MAX`, `ADDRESS`, `LINK`) VALUE('{}', '{}', '{}', FALSE, {}, {}, '{}', '{}')".format(name, city, type_, area_pair[0], area_pair[1], address, link)
        my.execute(cnx, sql1)
        id_ = my.last_insert_id(cnx)
        if id_ == -1:
            print("Can not get last insert id.")
            exit(1)
    if housing_estate_record_exists_for_date(cnx, id_, date_) == False:
        sql = "INSERT INTO `HOUSING_ESTATE_PRICE`(`HOUSING_ESTATE_ID`, `STATUS`, `PRICE`, `UNIT`, `DATE`) VALUE({}, '{}', {}, '{}', '{}')".format(id_, status, average_price, price_unit.strip(), date_)
        my.execute(cnx, sql)

def real_get_data(cnx, driver, page, path, city, date_):
    path = path + page +"/"
    print("Get Data from path: " + path)
    driver.get(path)
    parent = driver.find_element_by_css_selector("[class='resblock-list-wrapper']")
    sections = parent.find_elements_by_css_selector("[class='resblock-desc-wrapper']")
    # lsts = []
    for s in sections:
        name_element = s.find_element_by_class_name("name ")
        name = name_element.text
        link = name_element.get_attribute('href')
        type_ = s.find_element_by_class_name("resblock-type").text
        status = s.find_element_by_class_name("sale-status").text
        area = s.find_element_by_class_name("resblock-area").text
        address_element = s.find_element_by_class_name("resblock-location")
        address = address_element.find_element_by_tag_name('a').text

        price = s.find_element_by_class_name("resblock-price")
        average_price = price.find_element_by_class_name("number").text
        # 判断average_price是否为数字
        if average_price.isdigit() == False:
            average_price = -1
        price_unit = ""
        try:
            price_unit = price.find_element_by_class_name("desc").text
        except:
            price_unit = "未知"
        # total_price = ""
        # try:
        #     total_price = price.find_element_by_class_name("second").text
        # except:
        #     total_price = "-1"
        store_housing_estate_price(cnx, name, city, type_, status, area, average_price,
                                   price_unit, address, link, date_)
    cnx.commit()
        # lst = [name, type, status, area, average_price, price_unit, total_price, address, link]
        # lsts.append(lst)
    # return lsts

## count house
def house_num(driver, path):
    driver.get(path)
    num = driver.find_element_by_class_name("resblock-have-find")
    return num.find_element_by_class_name("value").text

# set citys to look
def citys():
    return {"南昌":"https://nc.fang.lianjia.com/loupan/", "上海":"https://sh.fang.lianjia.com/loupan/xuhui-huangpu-changning-putuo-pudong-baoshan-hongkou-yangpu-minhang-jiading-songjiang-qingpu-fengxian-jinshan-chongming/"}

def query_houses_price(driver, city, date_):
    cnx = my.open_mysql_connection("127.0.0.1", 3306, "root", "1qaz2wsx")
    cnx.autocommit = True
    my.use_database(cnx, "WHEREISMYHOME")
    path = city[1]
    house_count = int(house_num(driver, path))
    pages = house_count / 10
    if house_count % 10 != 0:
        pages += 1
    page_index = 1
    while page_index <= pages:
        page = "pg" + str(page_index)
        real_get_data(cnx, driver, page, path, city[0], date_)
        page_index += 1
    my.close_mysql_connection(cnx)


def webdriver_init():
    option = webdriver.ChromeOptions()
    option.add_argument("headless")
    option.add_argument("start-maximized")
    option.add_argument("disable-infobars")
    option.add_argument("--disable-extensions")
    option.add_argument("--disable-gpu")
    option.add_argument("--disable-dev-shm-usage")
    option.add_argument("--no-sandbox");
    return option

if __name__ == '__main__':
    option = webdriver_init()
    driver = webdriver.Chrome(chrome_options=option)
    citys_ = citys()
    # file_lst = []
    date_ = get_date()
    for city in citys_.items():
        query_houses_price(driver, city, date_)
    driver.close()
    driver.quit()
