from pymongo import MongoClient
from s_lib import setup_mongo, setup_mecab

def rename(db):
    col = db["result"]
    col.update({}, { "$rename": { "count_of_kill": "kill_count_2" } }, False, True)

def main():
    db = setup_mongo('ika-db')

    rename(db)

main()
