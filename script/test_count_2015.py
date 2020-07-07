# -*- coding: utf-8 -*-
from pymongo import MongoClient
from s_lib import setup_mongo, setup_mecab
from datetime import datetime
from datetime import timedelta

"""
count_2015.pyのテスト用短縮版
"""

def daterange(_start, _end):
    for n in range((_end - _start).days):
        yield _start + timedelta(n)

def count(db, flag):
    # 日毎に、与えられたflagフィールドが1のdocumentをカウントする。
    # 返すリストの要素は"day'\t'month'\t'count"の文字列
    all_day_list = []

    start = datetime.strptime('2015-02-17', '%Y-%m-%d')
    end = datetime.strptime('2015-12-31', '%Y-%m-%d')

    for date in daterange(start, end):
        today = date.isoformat()
        next_day = (date + timedelta(days=1)).isoformat()

        where = {
            flag : 1,
            'created_at_iso': {
                '$gte': today,
                '$lt': next_day
            }
        }

        month = str(date.month).zfill(2)
        day = str(date.day).zfill(2)

        col = db['2015-' + month]
        one_day_count = col.find(where).count()

        one_day = '\t'.join([month, day, str(one_day_count)])
        all_day_list.append(one_day)

    return all_day_list

def count_all(db):
    # 日毎に、icho, kaede, othersのいずれかのフラグが1のdocumentをカウントする。
    # 返すリストの要素は"day'\t'month'\t'count"の文字列
    all_day_list = []

    start = datetime.strptime('2015-02-17', '%Y-%m-%d')
    end = datetime.strptime('2015-12-31', '%Y-%m-%d')

    for date in daterange(start, end):
        today = date.isoformat()
        next_day = (date + timedelta(days=1)).isoformat()

        where = {
            '$or': [ {'icho': 1}, {'kaede': 1}, {'others': 1} ],
            'created_at_iso': {
                '$gte': today,
                '$lt': next_day
            }
        }

        month = str(date.month).zfill(2)
        day = str(date.day).zfill(2)

        col = db['2015-' + month]
        one_day_count = col.find(where).count()

        one_day = '\t'.join([month, day, str(one_day_count)])
        all_day_list.append(one_day)

    return all_day_list

def main():
    result_dir = '/now24/naruse/out/'

    db_hk = setup_mongo('2015_hk_twi_1208')

    dbs = [db_hk]
    prefecture_list = ["hk"]
    flag_list = ["others"]

    for db, pre in zip(dbs, prefecture_list):
        for flag in flag_list:
            m_d_count_list = count(db, flag)
            filename = "daily_count_" + pre + "_" + flag + ".tsv"
            with open(result_dir+filename, "w") as f:
                f.write("\n".join(m_d_count_list))
        """m_d_count_list = count_all(db)
        filename = "daily_count_" + pre + "_all.tsv"
        with open(result_dir+filename, "w") as f:
            f.write("\n".join(m_d_count_list))"""

main()
