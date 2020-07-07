"""
2015年のフィールド名koyoをothersにrenameするscripts
"""

from pymongo import MongoClient
from s_lib import setup_mongo, setup_mecab

def rename(db):
    for month in range(2, 13): # 2015年には1月のデータがない(2/17~のデータ)
        month = str(month).zfill(2)
        col = db["2015-" + month]

        col.update({}, { "$rename": { "koyo": "others" } }, false, true)

        print("###\t" + month + "月完了")

def main():
    db_tk = setup_mongo('2015_tk_twi')
    db_hk = setup_mongo('2015_hk_twi_1208')
    db_is = setup_mongo('2015_is_twi')

    dbs = [db_tk, db_hk, db_is]

    for db in dbs:
        rename(db)


main()
