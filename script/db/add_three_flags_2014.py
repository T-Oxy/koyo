"""
既存のDB:
    2014_twi
に、イチョウ・カエデ・紅葉キーワードが含まれているか判定するflagとなるフィールドを追加するスクリプト
"""
from pymongo import MongoClient
from s_lib import setup_mongo, setup_mecab

def add_flags(db, pname_list, keywords, f_name):
    for pname in pname_list:
        for month in range(1, 13):
            month = str(month).zfill(2)
            col = db["2014_" + month + pname]

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

    db = setup_mongo('2014_twi')
    pname_list = ['hk', 'tk', 'is']

    add_flags(db, pname_list, icho, "icho")
    add_flags(db, pname_list, kaede, "kaede")
    add_flags(db, pname_list, koyo, "koyo")

main()
