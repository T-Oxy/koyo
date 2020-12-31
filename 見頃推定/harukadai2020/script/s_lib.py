import MeCab
from pymongo import MongoClient, DESCENDING

def setup_mongo(db_name):
  connection = MongoClient()
  db = connection[db_name]
  print('mongoDB ready')
  return db

def setup_mecab(dic_path):
  mecab = MeCab.Tagger('-d ' + dic_path)
  mecab.parse('')
  """
  パーサーにデータを渡す前にこれを挟むことで、
  UnicodeDecodeErrorを避けることが出来る、らしい。
  """
  print('mecab ready')
  return mecab
