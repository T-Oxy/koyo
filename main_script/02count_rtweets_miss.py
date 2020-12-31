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

numofclasses = "4"

icho = ["いちょう", "イチョウ", "銀杏"]
kaede = ["かえで", "カエデ", "楓"]
sonota = ["こうよう", "もみじ", "紅葉", "黄葉", "コウヨウ", "モミジ"]
koyo = icho + kaede + sonota

keywords = {
    "icho": icho,
    "kaede": kaede,
    "sonota": sonota,
    "koyo": koyo
}

def date_range(start, end):
    for n in range((end - start).days + 1):
        yield start + timedelta(n)

def read_relation_words(pref, flag):
    rwords_dir = "/now24/naruse/koyo/result/related_words_miss/"
    fname = f"{flag}_{pref}_{numofclasses}soa.txt"
    fpath = rwords_dir + fname

    df = pd.read_csv(fpath, names=('word', 'soa'), header=None)
    # 関連度が正でないものは捨てる
    relation_words = df[df.soa > 0].word.tolist()
    return relation_words

def count_rtweets(pref, db, flag, relation_words, fixed_num):
    JST = dt.timezone(dt.timedelta(hours=9))
    start = dt.datetime(2015, 8, 15, tzinfo=JST)
    end = dt.datetime(2015, 12, 31, tzinfo=JST)
    num_of_rwords = len(relation_words)

    """
    # 関連語の数を割合で定める場合
    limit = round(num_of_rwords * (rate / 100))
    limited_words = set(relation_words[0:limit]) | set(keywords[flag])
    """

    # 関連語の数を固定数で定める場合
    if num_of_rwords < fixed_num:  # 関連後数 < 固定数の場合、とりあえず全て使う。
        fixed_num = num_of_rwords

    limited_words = set(relation_words[0:fixed_num]) | set(keywords[flag])

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
            if len(set(tw['morpho_text'].split()) & limited_words) > 0:
                count += 1

        one_day_counts = date.date().isoformat() + '\t' + str(count)
        all_day_counts.append(one_day_counts)

    return all_day_counts

def main():
    db_tk = setup_mongo('2015_tk_twi')
    db_hk = setup_mongo('2015_hk_twi_1208')
    db_is = setup_mongo('2015_is_twi')

    dbs = [("tk", db_tk), ("hk", db_hk), ("is", db_is)]
    flags = ["icho", "kaede", "sonota", "koyo"]

    fixed_nums = [50, 150, 250, 500] # 東京の関連語数の1%, 5%, 10%とテキトーに250

    result_dir = '/now24/naruse/koyo/result/rtweets_count_miss/'

    for pref, db in tqdm(dbs, desc="DB(pref)"):
        for flag in tqdm(flags, desc="flag"):
            relation_words = read_relation_words(pref, flag)
            for fixed_num in tqdm(fixed_nums, desc="fixed_nums"):
                all_day_counts = count_rtweets(pref, db, flag, relation_words, fixed_num)

                os.makedirs(result_dir, exist_ok=True)
                fname = f"{pref}_{flag}_{str(fixed_num).zfill(3)}rwords_count.txt"
                with open(result_dir+fname, "w") as f:
                    f.write("\n".join(all_day_counts))

    print(f"{result_dir} に出力しました。")

main()
