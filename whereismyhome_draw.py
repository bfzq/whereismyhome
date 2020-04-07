#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import mysql_tool as my

def get_data(cnx):
    sql = "select name, price,`date` from HOUSING_ESTATE he left join HOUSING_ESTATE_PRICE hep on he.id = hep.HOUSING_ESTATE_ID where he.city = '南昌' and he.type ='住宅' and hep.STATUS = '在售' and hep.price > 0 and hep.unit like '元/平%' order by name;"

if __name__ == '__main__':
