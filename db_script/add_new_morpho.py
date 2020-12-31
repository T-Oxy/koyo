# -*- coding: utf-8 -*-
"""
既存のDBにはツイートの動詞と名詞の形態素フィールドしか無い
そこで副詞と形容詞を追加した新しいフィールドmorphos_4classを作成するスクリプト
"""
import MeCab
from tqdm import tqdm
from pymongo import MongoClient
from s_lib import setup_mongo, setup_mecab

def add_new_morpho(col, mecab):
    twis = col.find()

    for twi in twis:
        morphos = []
        text = twi['text']
        node = mecab.parseToNode(text)

        while node:
            word_class = node.feature.split(',')
            if word_class[0] in ['名詞', '動詞', '形容詞', '副詞']:
                if word_class[6] == '*': #原型はデータが入ってない場合がある
                    base = node.surface
                else:
                    base = word_class[6]
                morphos.append(base) # 動詞の原型を入れていく
            node = node.next

        morphos = list(set(morphos)) # 重複を削除
        col.update_one({'_id': twi['_id']}, {'$set': {"morphos_4class": (" ").join(morphos)}})


def main():
    neologd_path = '/now24/naruse/local/mecab/lib/mecab/dic/mecab-ipadic-neologd'
    mecab = setup_mecab(neologd_path)

    db_name = "2014_twi"
    db = setup_mongo(db_name)

    prefs = ["is", "hk", "tk"]
    months = range(1, 13)
    for pref in tqdm(prefs):
        for month in tqdm(months):
            month = str(month).zfill(2)
            col = db["2014_" + str(month) + "_" + pref]
            add_new_morpho(col, mecab)

main()
