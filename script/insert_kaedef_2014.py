"""
既存の桜DBに、紅葉キーワードが含まれているか判定するflagとなるフィールドを追加するスクリプト
"""
from pymongo import MongoClient
from s_lib import setup_mongo, setup_mecab

keywords = ["かえで", "カエデ", "楓"]

db = setup_mongo('2014_sakura_twi_1208')
pname_list = ['hk', 'tk', 'is']

for pname in pname_list:
    col = db['season_' + pname]

    for post in col.find():
        mors = post['morpho_text'].split(" ")
        if len(set(keywords) & set(mors)) > 0:
            col.update_one({'_id':post['_id']}, {'$set':{"kaede":1}})
        else:
            col.update_one({'_id':post['_id']}, {'$set':{"kaede":0}})
