#!/usr/local/bin/python

import mysql.connector
from mysql.connector import errorcode

def open_mysql_connection(host, port, user, passwd):
    try:
        cnx = mysql.connector.connect(host=host, user=user,
                                      password=passwd, port=port)
        return cnx
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database dos not exist")
        else:
            print(err)

def close_mysql_connection(cnx):
    cnx.close()

def use_database(cnx, DB_NAME):
    cursor = cnx.cursor()
    try:
        cursor.execute("use {}".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Database {} does not exists.".format(DB_NAME))
    cursor.close()

def execute(cnx, sql):
    cursor = cnx.cursor()
    try:
        cursor.execute(sql)
    except mysql.connector.Error as err:
        print("{}.SQL : {}".format(err, sql))
    cursor.close()

def last_insert_id(cnx):
    cursor = cnx.cursor()
    try:
        cursor.execute("SELECT LAST_INSERT_ID()")
        for row in cursor:
            return row[0]
    except mysql.connector.Error as err:
        print("{}.SQL : SELECT LAST_INSERT_ID()".format(err, ))
    cursor.close()
    return -1

def query(cnx, sql):
    cursor = cnx.cursor()
    data = []
    try:
        cursor.execute(sql)
        for row in cursor:
            data.append(row)
    except mysql.connector.Error as err:
        print("{}.SQL : {}".format(err, sql))
    cursor.close()
    return data

# if __name__ == '__main__':
#     cnx = open_mysql_connection("127.0.0.1", 3306, "root", "1qaz2wsx")
#     # execute(cnx, "create database test1");
#     use_database(cnx, "test1")
#     # execute(cnx, "create table test3(id int)")
#     execute(cnx, "insert into test3(id) value(1111)")
#     cnx.commit()
#     data = query(cnx, "select * from test3")
#     print(data)
#     close_mysql_connection(cnx)
