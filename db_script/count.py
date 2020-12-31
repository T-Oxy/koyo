# -*- coding: utf-8 -*-
from pymongo import MongoClient
from s_lib import setup_mongo, setup_mecab
import datetime as dt


JST = dt.timezone(dt.timedelta(hours=9))
CORRECT = {
"tk": [dt.datetime(2014, 11, 25, tzinfo=JST), dt.datetime(2014, 12, 18, tzinfo=JST)],
"hk": [dt.datetime(2014, 10, 30, tzinfo=JST), dt.datetime(2014, 11, 3, tzinfo=JST)],
"is": [dt.datetime(2014, 11, 13, tzinfo=JST), dt.datetime(2014, 11, 29, tzinfo=JST)]
}

def main():
    db = setup_mongo('2014_koyo_twi')
    col = db["tk"]

    """where = {
        'created_at_iso': {
            '$gte': CORRECT["tk"][0].isoformat(),
            '$lte': CORRECT["tk"][1].isoformat() # 12/18の0時までになっている．
        }
    }
    where = { "$or": [
        {'created_at_iso': {'$lt': CORRECT["tk"][0].isoformat()}},
        {'created_at_iso': {'$gt': CORRECT["tk"][1].isoformat()}}
        ]}
        """
    where = {
        'created_at_iso': {'$gt': CORRECT["tk"][1].isoformat()}
        }

    count = col.find(where).count()
    ex1 =  col.find_one(where)

    print(f"count: {count}")
    print(ex1)

main()
