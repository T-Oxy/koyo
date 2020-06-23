"""
既存の桜DBに、紅葉キーワードが含まれているか判定するflagとなるフィールドを追加するスクリプト
"""
from pymongo import MongoClient
from s_lib import setup_mongo, setup_mecab

keywords = ["いちょう", "イチョウ", "銀杏"]

db = setup_mongo('2015_tk_twi')
pname_list = ['tk'] # 'hk', 'is']

for pname in pname_list:
    for month in range(2, 13):
        month = str(month).zfill(2)

        col = db["2015-"+month]

        for post in col.find():
            mors = post['morpho_text'].split(" ")
            if len(set(keywords) & set(mors)) > 0:
                col.update_one({'_id':post['_id']}, {'$set':{"icho":1}})
            else:
                col.update_one({'_id':post['_id']}, {'$set':{"icho":0}})


                
