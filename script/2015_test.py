"""
add_three_flags_2015.pyのテスト版(北海道の2月にのみ)
"""
from pymongo import MongoClient
from s_lib import setup_mongo, setup_mecab

def add_flags(db, keywords, f_name):
    for month in range(2, 3): # 2015年には1月のデータがない
        month = str(month).zfill(2)
        col = db["2015-" + month]

        for post in col.find():
            mors = post['morpho_text'].split(" ")
            if len(set(keywords) & set(mors)) > 0:
                col.update_one({'_id':post['_id']}, {'$set':{f_name:1}})
            else:
                col.update_one({'_id':post['_id']}, {'$set':{f_name:0}})

        print("###\t" + month + "月への書き込み完了")

def main():
    icho = ["いちょう", "イチョウ", "銀杏"]
    kaede = ["かえで", "カエデ", "楓"]
    koyo = ["こうよう", "もみじ", "紅葉", "黄葉", "コウヨウ", "モミジ"]

    db_tk = setup_mongo('2015_tk_twi')
    db_hk = setup_mongo('2015_hk_twi_1208')
    db_is = setup_mongo('2015_is_twi')

    dbs = [db_hk]

    for db in dbs:
        add_flags(db, icho, "icho")
        add_flags(db, kaede, "kaede")
        add_flags(db, koyo, "koyo")

main()
