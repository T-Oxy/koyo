"""
2014年のフィールド名koyoをsonotaにrenameするスクリプト
"""
from tqdm import tqdm
from pymongo import MongoClient
from s_lib import setup_mongo, setup_mecab

def main():
    db = setup_mongo('2014_twi')
    prefs = ["tk", "hk", "is"]
    months = range(1, 13)

    for pref in tqdm(prefs):
        for month in tqdm(months):
            month = str(month).zfill(2)
            col = db["2014_" + month + "_" + pref]
            col.update_many({}, { "$rename": { "koyo": "sonota" } }, False)
            # 第3引数でupsertをしないようにしている。(省略も可。defaultでもFalse)
main()
