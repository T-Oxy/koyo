# -*- coding: utf-8 -*-
"""
単純に対象語が含まれているツイート数を日次にカウントし、記録するスクリプト
"""
import os
import datetime as dt
from datetime import timedelta
import pandas as pd
from tqdm import tqdm
from pymongo import MongoClient
from s_lib import setup_mongo, setup_mecab

icho = ["いちょう", "イチョウ", "銀杏"]
kaede = ["かえで", "カエデ", "楓"]
sonota = ["こうよう", "もみじ", "紅葉", "黄葉", "コウヨウ", "モミジ"]
koyo = icho + kaede + sonota

target_words = {"icho": set(icho), "kaede": set(kaede), "sonota": set(sonota), "koyo": set(koyo)}

"""target_words = { \
"icho": {"いちょう", "イチョウ", "銀杏"}, \
"kaede": {"かえで", "カエデ", "楓"}, \
"sonota": {"こうよう", "もみじ", "紅葉", "黄葉", "コウヨウ", "モミジ"}, \
"koyo": set(koyo)
}"""

def date_range(start, end):
    for n in range((end - start).days + 1):
        yield start + timedelta(n)

def count_simply(db, flag):
    JST = dt.timezone(dt.timedelta(hours=9))
    # start = dt.datetime(2015, 8, 15, tzinfo=JST)
    start = dt.datetime(2015, 2, 17, tzinfo=JST)
    end = dt.datetime(2015, 12, 31, tzinfo=JST)

    month = "01"
    all_day_counts = []
    for date in date_range(start, end):
        today = date.isoformat()
        next_day = (date + dt.timedelta(days=1)).isoformat()

        where = {
        'created_at_iso':
            {
            '$gte': today,
            '$lt': next_day
            }
        }

        #collectionが月ごとに作成されているため、月が変わるごとにcollectionを移動
        current_month = str(date.month).zfill(2)
        if month != current_month:
            month = current_month
            col = db['2015-' + month]

        oneday_tws = col.find(where)
        count = 0
        for tw in oneday_tws:
            if len(set(tw['morpho_text'].split()) & target_words[flag]) > 0:
                count += 1

        one_day_counts = date.date().isoformat() + '\t' + str(count)
        all_day_counts.append(one_day_counts)

    return all_day_counts

def main():
    db_tk = setup_mongo('2015_tk_twi')
    db_hk = setup_mongo('2015_hk_twi_1208')
    db_is = setup_mongo('2015_is_twi')

    dbs = [("tk", db_tk), ("hk", db_hk), ("is", db_is)]
    flags = ["icho", "kaede", "sonota", "koyo"] # sonota

    result_dir = '/now24/naruse/koyo/endo/result/simple_count/'

    for pref, db in tqdm(dbs, desc="DB(pref)"):
        for flag in tqdm(flags, desc="flag"):

            all_day_counts = count_simply(db, flag)
            os.makedirs(result_dir, exist_ok=True)
            fname = f"{pref}_{flag}_count.txt"
            with open(result_dir+fname, "w") as f:
                f.write("\n".join(all_day_counts))

    print(f"{result_dir} に出力しました。")

main()
