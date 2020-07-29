from pymongo import MongoClient
from s_lib import setup_mongo, setup_mecab
from tqdm import tqdm

"""
2014のtwiから、県ごとの10月11月12月だけのデータベースを作るスクリプト
"""

def cut_month(fromdb, todb):
    prefs = ["tk", "hk", "is"]
    mons = [10, 11, 12]

    for pref in tqdm(prefs):
        tocol = todb[pref]
        for mon in mons:
            fromcol = fromdb["2014_" + str(mon) + "_" + pref]
            docs = fromcol.find()
            for i in docs:
                tocol.insert(i)

def main():
    fromdb = setup_mongo('2014_twi')
    todb = setup_mongo('2014_OctNovDec_twi')
    cut_month(fromdb, todb)

main()
