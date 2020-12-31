# -*- coding: utf-8 -*-
from pymongo import MongoClient
from s_lib import setup_mongo, setup_mecab
import datetime as dt
from tqdm import tqdm

"""
2014のtwiから、正解期間のツイートだけが入ったデータベースを作成するスクリプト

をただカウントだけにしたもの
"""

JST = dt.timezone(dt.timedelta(hours=9))
correct = {
"tk": [dt.datetime(2014, 11, 25, tzinfo=JST), dt.datetime(2014, 12, 18, tzinfo=JST)],
"hk": [dt.datetime(2014, 10, 30, tzinfo=JST), dt.datetime(2014, 11, 3, tzinfo=JST)],
"is": [dt.datetime(2014, 11, 13, tzinfo=JST), dt.datetime(2014, 11, 29, tzinfo=JST)]
}

def daterange(start_end):
    start = start_end[0]
    end = start_end[1]
    for n in range((end - start + dt.timedelta(days=1)).days):
        yield start + dt.timedelta(n)

def count_extract_day(fromdb):
    prefs = ["tk"] # "is", "hk",\
    month = 0
    count = 0

    for pref in tqdm(prefs):
        for day in daterange(correct[pref]):
            if month != day.month:
                month = day.month
                fromcol = fromdb["2014_" + str(month) + "_" + pref]

            today = day.isoformat()
            next_day = (day + dt.timedelta(days=1)).isoformat()
            where = {
                'created_at_iso': {
                    '$gte': today,
                    '$lt': next_day
                }
            }

            # 'created_at_iso'は文字列なので，単純に比較できない？
            count += fromcol.find(where).count()
            print(f"count: {count}")

def main():
    fromdb = setup_mongo('2014_twi')
    count_extract_day(fromdb)

main()
