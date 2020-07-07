# -*- coding: utf-8 -*-
from pymongo import MongoClient
from s_lib import setup_mongo, setup_mecab
from datetime import datetime
from datetime import timedelta

"""
2015年のDBから、日毎の総ツイート数をカウントし、ファイルに出力する。

出力フォーマット:
    [月 日 その日の総ツイート数]

出力ファイル名：
・daily_count_<県>_all.tsv"

※flagとallで別れたスクリプトになっているのは、単にallの数え忘れを後から気づいたため。
"""

def daterange(_start, _end):
    for n in range((_end - _start).days):
        yield _start + timedelta(n)

def count_all(db):
    # 日毎のdocument数(=総ツイート数)をカウントする。
    # 返すリストの要素は"day'\t'month'\t'count"の文字列
    all_day_list = []

    start = datetime.strptime('2015-02-17', '%Y-%m-%d')
    end = datetime.strptime('2015-12-31', '%Y-%m-%d')

    for date in daterange(start, end):
        today = date.isoformat()
        next_day = (date + timedelta(days=1)).isoformat()

        month = str(date.month).zfill(2)
        day = str(date.day).zfill(2)

        col = db['2015-' + month]
        one_day_count = col.find().count()

        one_day = '\t'.join([month, day, str(one_day_count)])
        all_day_list.append(one_day)

    return all_day_list

def main():
    result_dir = '/now24/naruse/out/'

    db_tk = setup_mongo('2015_tk_twi')
    db_hk = setup_mongo('2015_hk_twi_1208')
    db_is = setup_mongo('2015_is_twi')

    dbs = [db_tk, db_hk, db_is]
    prefecture_list = ["tk", "hk", "is"]

    for pre, db in zip(prefecture_list, dbs):
        m_d_count_list = count_all(db)
        filename = "daily_count_" + pre + "_all.tsv"
        with open(result_dir+filename, "w") as f:
            f.write("\n".join(m_d_count_list))

main()
