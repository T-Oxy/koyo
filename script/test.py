from pymongo import MongoClient
from s_lib import setup_mongo, setup_mecab

def test(db):
    col = db["season_hk"]
    find = col.find()
    for i in find:
        col.insert(i)

def main():
    db = setup_mongo('2014_sakura_twi_1208')
    test(db)

main()
