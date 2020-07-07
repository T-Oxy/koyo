from pymongo import MongoClient
from s_lib import setup_mongo, setup_mecab

def rename(db):
    col = db["result"]
    col.update_many({}, { "$rename": { "kill_count_2": "kill_count" } })

def main():
    db = setup_mongo('ika-db')

    rename(db)

main()
