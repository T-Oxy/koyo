"""
既存のDB:
    2015_hk_twi_1208
    2015_is_twi
    2015_tk_twi
のツイートに「いちょう」、「かえで」、「その他」が含まれているか判定するflagのフィールドを追加するスクリプト

※2014年版との違い:
    2014と2015ではDBの構造が違う。
    各地域ごとにDBがあるので、2014にあったpname_listでの地域指定がない。
    1月のデータがない。
"""
from pymongo import MongoClient
from s_lib import setup_mongo, setup_mecab

def add_flags(db, keywords, f_name):
    for month in range(2, 13): # 2015年には1月のデータがない(2/17~のデータ)
        month = str(month).zfill(2)
        col = db["2015-" + month]

        for post in col.find():
            mors = post['morpho_text'].split(" ")
            if len(set(keywords) & set(mors)) > 0:
                col.update_one({'_id':post['_id']}, {'$set':{f_name:1}})
            else:
                col.update_one({'_id':post['_id']}, {'$set':{f_name:0}})

        print("###\t" + month + "月完了: " + f_name + ' of ' + pname)

def main():
    icho = ["いちょう", "イチョウ", "銀杏"]
    kaede = ["かえで", "カエデ", "楓"]
    others = ["こうよう", "もみじ", "紅葉", "黄葉", "コウヨウ", "モミジ"]

    db_tk = setup_mongo('2015_tk_twi')
    db_hk = setup_mongo('2015_hk_twi_1208')
    db_is = setup_mongo('2015_is_twi')

    dbs = [db_tk, db_hk, db_is]

    for db in dbs:
        add_flags(db, icho, "icho")
        add_flags(db, kaede, "kaede")
        add_flags(db, koyo, "others")

main()
