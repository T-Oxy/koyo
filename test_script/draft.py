import os
from s_lib import setup_mongo
import sys, math, collections
from tqdm import tqdm

sakura = ['桜', 'さくら', 'サクラ']
icho = ["いちょう", "イチョウ", "銀杏"]
kaede = ["かえで", "カエデ", "楓"]
sonota = ["こうよう", "もみじ", "紅葉", "黄葉", "コウヨウ", "モミジ"]
koyo = icho + kaede + sonota

def calc_pmi(sw, w, s, N):
  pmi = math.log2(((sw + 1) * N) / (w * s))
  return(pmi)

def calc_soa(sw, ns_w, w, s, ns, N):
    #  soa = math.log2(((sw + 1) * ns)/((ns_w + 1) * s))
    soa = calc_pmi(sw, w, s, N) - calc_pmi(ns_w, w, ns, N)
    return(soa)

class RelatedWords:
    def __init__(self, target, pref, kind, num_class):
        self.target = ""
        self.pref = ""
        self.kind = ""
        self.num_class = num_class
        self.words = []

class RelatedWordsGetter:
    def __init__(self, db):
        self.db = db

    def target_set(keywords, pref, num_class):
        self.keywords = keywords
        pmi = RelatedWords(target, pref, "pmi", num_class)
        soa = RelatedWords(target, pref, "soa", num_class)

        col = db[pref]
        s_twis = list(col.find(season_pipe))
        ns_twis = list(col.find(unseason_pipe))

    def get(option):
        if self.keywords =  koyo:
            season_pipe = {'$or': [ {'icho': 1}, {'kaede': 1}, {'sonota': 1} ]}
            unseason_pipe = { '$and': [ {'icho': 0}, {'kaede': 0}, {'sonota': 0} ]}


        swords = []
        n_and_s_words = {}
        for s_twi in s_twis:
            swords.extend(s_twi['morphos_4class'].split(' '))
        uniq_swords = list(set(swords))
        for ns_twi in ns_twis:
            morpho = ns_twi['morphos_4class'].split(' ')
            for w in uniq_swords:
                if w in morpho:
                    n_and_s_words[w] = n_and_s_words[w] + 1 if w in n_and_s_words else 1

        swords_count = collections.Counter(swords) # season_wordの出現回数のカウントをした。
        N = len(s_twis) + len(ns_twis)

        pmi_of_word = {}
        for sword, count in swords_count.items():
            if sword in keywords[flag]: #対象語のpmiの計算を飛ばす
                continue
            count_in_stwis = count
            count_in_nstwis = n_and_s_words[sword] if sword in n_and_s_words else 0
            count_in_all = count_in_stwis + count_in_nstwis
            if not any([count_in_all < 1, len(s_twis) < 1]):
                pmi_of_word[sword] = calc_pmi(count_in_stwis, count_in_all, len(s_twis), N)

        sorted_pmi = sorted(pmi_of_word.items(), key=lambda x:x[1], reverse=True)

        soa_of_word = {}
        for sword, count in swords_count.items():
            if sword in keywords[flag]: #対象語のsoaの計算を飛ばす
                continue
            count_in_stwis = count
            count_in_nstwis = n_and_s_words[sword] if sword in n_and_s_words else 0
            count_in_all = count_in_stwis + count_in_nstwis
            if not any([count_in_all < 1, len(s_twis) < 1, len(ns_twis) < 1]):
                soa_of_word[sword] = calc_soa(count_in_stwis, count_in_nstwis, count_in_all, len(s_twis), len(ns_twis), N)

        sorted_soa = sorted(soa_of_word.items(), key=lambda x:x[1], reverse=True)



        self.pmi =




        if option == 1:
            return self.soa
        elif option == 2:
            return self.pmi, self.soa

def mywrite(related_words, dir):
    os.makedirs(dir, exist_ok=True)
    with open(dir + f'{related_words.target}_{related_words.pref}_{relatedwords.num_class}{relatedwords.kind}.txt', 'w') as f:
        for word, strength in related_words.words:
            f.write(f'{word}, {strength}\n')

def main():
    db = setup_mongo('naruse_2014)
    getter = RelatedWordsGetter(db)

    getter.set_target(koyo, "tokyo", 4)
    pmi, soa = getter.get(2)

    # result_dir = "/now24/naruse/koyo/result/related_words/"
    result_dir = "/Users/daigo/workspace/koyo/test/"
    mywrite(pmi, result_dir)
    mywrite(soa, result_dir)

main()







    for flag in tqdm(flags, desc="flag"):
        if flag == "koyo":
            season_pipe = {'$or': [ {'icho': 1}, {'kaede': 1}, {'sonota': 1} ]}
            unseason_pipe = { '$and': [ {'icho': 0}, {'kaede': 0}, {'sonota': 0} ]}

        for pref in tqdm(prefs, desc="pref"):
            col = db[pref]
            """col = db['season_' + pref]"""

            s_twis = list(col.find(season_pipe))
            ns_twis = list(col.find(unseason_pipe))
            # s_twis: 旬ツイートのリスト
            # ns_twis: 非旬ツイートのリスト

            """
            s_twis = list(col.find({'sakura_twi': 1}))
            ns_twis = list(col.find({'sakura_twi': 0}))
            """

            swords = []
            n_and_s_words = {}
            for s_twi in s_twis:
                swords.extend(s_twi['morphos_4class'].split(' '))
            uniq_swords = list(set(swords))
            for ns_twi in ns_twis:
                morpho = ns_twi['morphos_4class'].split(' ')
                for w in uniq_swords:
                    if w in morpho:
                        n_and_s_words[w] = n_and_s_words[w] + 1 if w in n_and_s_words else 1

            # swords(旧:words): 旬ツイートに含まれていた語のリスト。重複あり
            # uniq_swords(旧:uwords): 旬ツイートに含まれていた語のリスト。重複なし
            # n_and_s_words(旧:ns_words): 非旬ツイート && 旬ツイートに含まれている語がkeyでその出現数がvalue

            swords_count = collections.Counter(swords) # season_wordの出現回数のカウントをした。
            N = len(s_twis) + len(ns_twis)

            # swords_count(旧:sw_count): 旬ツイートの語がkeyで、出現回数がvalue
            # len(s_twis)(旧:s): 旬ツイートの数
            # len(ns_twis)(旧:ns): 非旬ツイートの数
            # N: ツイート総数

            pmi_of_word = {}
            for sword, count in swords_count.items():
                if sword in keywords[flag]: #対象語のpmiの計算を飛ばす
                    continue
                count_in_stwis = count
                count_in_nstwis = n_and_s_words[sword] if sword in n_and_s_words else 0
                count_in_all = count_in_stwis + count_in_nstwis
                if not any([count_in_all < 1, len(s_twis) < 1]):
                    pmi_of_word[sword] = calc_pmi(count_in_stwis, count_in_all, len(s_twis), N)

            sorted_pmi = sorted(pmi_of_word.items(), key=lambda x:x[1], reverse=True)

            # count_in_stwis(旧:sw): 関連語の旬ツイートでの出現回数。
            # count_in_nstwis(旧:ns_w): 関連語の非旬ツイートでの出現回数。
            # count_in_all(旧:wc): 関連語の全ツイートでの出現回数。
            # sorted_pmi: keyが関連語、valueがそのpmiの辞書。pmiが大きい順

            soa_of_word = {}
            for sword, count in swords_count.items():
                if sword in keywords[flag]: #対象語のsoaの計算を飛ばす
                    continue
                count_in_stwis = count
                count_in_nstwis = n_and_s_words[sword] if sword in n_and_s_words else 0
                count_in_all = count_in_stwis + count_in_nstwis
                if not any([count_in_all < 1, len(s_twis) < 1, len(ns_twis) < 1]):
                    soa_of_word[sword] = calc_soa(count_in_stwis, count_in_nstwis, count_in_all, len(s_twis), len(ns_twis), N)

            sorted_soa = sorted(soa_of_word.items(), key=lambda x:x[1], reverse=True)
