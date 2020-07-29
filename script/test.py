from pymongo import MongoClient
from s_lib import setup_mongo, setup_mecab

def test(db):
    col = db["season_hk"]
    find = col.find()

    todb = setup_mongo('ika-db')
    tocol = todb["result"]
    for i in find:
        tocol.insert_one(i)

def main():
    db = setup_mongo('2014_sakura_twi_1208')
    test(db)

main()
