# -*- coding: utf-8 -*-
from pymongo import MongoClient
from s_lib import setup_mongo, setup_mecab
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from tqdm import tqdm

"""
2014年のカウントはいらないので、間違えて作ったスクリプト
（いらないというかget_relation_wordsでやっている？）

2014_koyo_twiのDBから、条件を満たす日毎のツイート数をカウントし、ファイルに出力する。

出力フォーマット:
    [月 日 その日のツイート数]

出力ファイル名：
・daily_count_<県>_<flag名>.tsv"
"""

def daterange(start_end):
    start = start_end[0]
    end = start_end[1]
    for n in range((end - start + dt.timedelta(days=1)).days):
        yield start + dt.timedelta(n)

def count(col, flag, pref):
    # 日毎に、与えられたflagフィールドが1のdocumentをカウントする。
    # 返すリストの要素は"day'\t'month'\t'count"の文字列
    all_day_list = []

    JST = dt.timezone(dt.timedelta(hours=9))
    correct = {
    "tk": [dt.datetime(2014, 11, 25, tzinfo=JST), dt.datetime(2014, 12, 18, tzinfo=JST)],
    "hk": [dt.datetime(2014, 10, 30, tzinfo=JST), dt.datetime(2014, 11, 3, tzinfo=JST)],
    "is": [dt.datetime(2014, 11, 13, tzinfo=JST), dt.datetime(2014, 11, 29, tzinfo=JST)]
    }

    for date in daterange(correct[pref]):
        today = date.isoformat()
        next_day = (date + timedelta(days=1)).isoformat()

        if flag == "total":
            where = {
                'created_at_iso': {
                    '$gte': today,
                    '$lt': next_day
                }
            }
        elif flag == "koyo":
            where = {
                '$or': [ {'icho': 1}, {'kaede': 1}, {'others': 1} ],
                'created_at_iso': {
                    '$gte': today,
                    '$lt': next_day
                }
            }
        else:
            where = {
                flag : 1,
                'created_at_iso': {
                    '$gte': today,
                    '$lt': next_day
                }
            }

        month = str(date.month).zfill(2)
        day = str(date.day).zfill(2)

        one_day_count = col.find(where).count()

        one_day = '\t'.join([month, day, str(one_day_count)])
        all_day_list.append(one_day)

    return all_day_list

def main():
    result_dir = '/now24/naruse/out/2014/'

    db = setup_mongo('2014_koyo_twi')

    flags = ["icho", "kaede", "sonota", "koyo", "total"]
    prefectures= [ "is", "hk", "tk"]

    for pref in prefectures:
        col = db[pref]
        for flag in tqdm(flags):
            m_d_count_list = count(col, flag, pref)
            filename = "daily_count_" + pref + "_" + flag + ".tsv"
            with open(result_dir+filename, "w") as f:
                f.write("\n".join(m_d_count_list))

main()
