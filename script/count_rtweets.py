"""
2015年のDBから、割合別の関連語を含むツイート数をカウント・ファイルに出力する。
出力ファイル名： <県>_<flag名>_soa<rate>_count.txt"
出力フォーマット: [ISO日付  ツイート数]
"""
# -*- coding: utf-8 -*-
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

keywords = {
    "icho": icho,
    "kaede": kaede,
    "sonota": sonota,
    "koyo": icho+kaede+sonota
}

def date_range(start, end):
    for n in range((end - start).days + 1):
        yield start + timedelta(n)

def read_relation_words(pref, flag):
    result_dir = "/now24/naruse/koyo/result/relation_words/"
    fname = pref + "_"+ flag + "_soa.txt"
    fpath = result_dir + fname

    df = pd.read_csv(fpath, names=('word', 'soa'), header=None)
    # 関連度が正でないものは捨てる
    relation_words = df[df.soa > 0].word.tolist()
    return relation_words

def count_rtweets(pref, db, flag, relation_words, rate):
    JST = dt.timezone(dt.timedelta(hours=9))
    start = dt.datetime(2015, 2, 17, tzinfo=JST)
    end = dt.datetime(2015, 12, 31, tzinfo=JST)
    num_of_rwords = len(relation_words)

    limit = round(num_of_rwords * (rate / 100))
    limited_words = set(relation_words[0:limit]) | set(keywords[flag])

    month = "01"
    all_day = []
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
        oneday_count = 0
        for tw in oneday_tws:
            if len(set(tw['morpho_text'].split()) & limited_words) > 0:
                oneday_count = oneday_count  + 1
                one_day = date.date().isoformat() + '\t' + str(oneday_count)
                all_day.append(one_day)

        return all_day

def main():
    db_tk = setup_mongo('2015_tk_twi')
    db_hk = setup_mongo('2015_hk_twi_1208')
    db_is = setup_mongo('2015_is_twi')

    dbs = [db_tk, db_hk, db_is]
    prefectures = ["tk", "hk", "is"]
    flags = ["icho", "kaede", "sonota", "koyo"]
    rates = range(10, 101, 10)

    result_dir = '/now24/naruse/koyo/result/relation_tweets_count/'

    for pref, db in zip(tqdm(prefectures), dbs):
        for flag in tqdm(flags):
            relation_words = read_relation_words(pref, flag)

            os.makedirs(result_dir, exist_ok=True)
            for rate in tqdm(rates):
                counts = count_rtweets(pref, db, flag, relation_words, rate)

                fname = pref + "_" + flag + "_soa" + str(rate) + "_count.txt"
                with open(result_dir+fname, "w") as f:
                    f.write("\n".join(counts))

main()
