from pymongo import MongoClient
from s_lib import setup_mongo, setup_mecab
from tqdm import tqdm

"""
2014のtwiから、県ごとの10月11月12月だけのデータベースを作るスクリプト
"""

def cut_month(fromdb, todb):
    prefs = ["tk", "hk", "is"]
    mons = [10, 11, 12]

    for pref in prefs:
        tocol = todb[pref]
        for mon in tqdm(mons):
            fromcol = fromdb["2014_" + str(mon) + "_" + pref]
            docs = fromcol.find()
            for i in docs:
                tocol.insert_one(i)

def main():
    fromdb = setup_mongo('2014_twi')
    todb = setup_mongo('2014_OctNovDec_twi')
    cut_month(fromdb, todb)

main()
