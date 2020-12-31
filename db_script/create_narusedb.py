# -*- coding: utf-8 -*-
from pymongo import MongoClient
from s_lib import setup_mongo, setup_mecab
import datetime as dt
from tqdm import tqdm

"""
2014_twiから2014_twi_naruseを作成する
スキーマ構造を
2014_twi_naruseでは、
 |-tk-全ツイートデータ（東京）
 |-hk-全ツイートデータ（北海道）
 |-is-全ツイートデータ（石川）
の形式にする。
"""

def move_tweets(fromdb, todb):
    prefs = ["is", "hk", "tk"]
    months = range(1, 13, 1)

    for pref in tqdm(prefs, desc="pref"):
        tocol = todb[pref]
        for month in months:
            fromcol = fromdb["2014_" + str(month).zfill(2)+ "_" + pref]
            twis = fromcol.find()
            tocol.insert_many(twis)

def main():
    fromdb = setup_mongo('2014_twi')
    todb = setup_mongo('2014_twi_naruse')
    move_tweets(fromdb, todb)

main()
