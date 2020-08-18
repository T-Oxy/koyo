"""
教師データのツイート内に含まれる各単語と
"イチョウ"の関連度を計算する
"""

import os
from s_lib import setup_mongo
import sys, math, collections
from tqdm import tqdm

icho = ["いちょう", "イチョウ", "銀杏"]
kaede = ["かえで", "カエデ", "楓"]
sonota = ["こうよう", "もみじ", "紅葉", "黄葉", "コウヨウ", "モミジ"]

keywords = {
    "icho": icho,
    "kaede": kaede,
    "sonota": sonota,
    "koyo": icho+kaede+sonota,
}

def calc_pmi(sw, w, s, N):
  pmi = math.log2(((sw + 1) * N) / (w * s))
  return(pmi)

def calc_soa(sw, ns_w, w, s, ns, N):
    #  soa = math.log2(((sw + 1) * ns)/((ns_w + 1) * s))
    soa = calc_pmi(sw, w, s, N) - calc_pmi(ns_w, w, ns, N)
    return(soa)

def main():
    db = setup_mongo('2014_koyo_twi')
    prefs = ["tk", "hk", "is"]
    flags = ["sonota", "koyo"] # ["icho", "kaede", "sonota", "koyo"]

    for flag in tqdm(flags):
        if flag == "koyo":
            season = {'$or': [ {'icho': 1}, {'kaede': 1}, {'koyo': 1} ]}
            unseason = { '$and': [ {'icho': 0}, {'kaede': 0}, {'koyo': 0} ]}
        elif flag == "sonota":
            season = { "koyo" : 1 }
            unseason = { "koyo" : 0 }

        for pref in prefs:
            col = db[pref]

            s_twis = list(col.find(season))
            ns_twis = list(col.find(unseason))

            words = []
            ns_words = {}
            for s_twi in s_twis:
                words.extend(s_twi['morpho_text'].split(' '))
            uwords = list(set(words))
            for ns_twi in ns_twis:
                morpho = ns_twi['morpho_text'].split(' ')
                for w in uwords:
                    if w in morpho:
                        ns_words[w] = ns_words[w] + 1 if w in ns_words else 1

            """
            words: 旬ツイートに含まれていた語のリスト。重複あり
            uwords: 旬ツイートに含まれていた語のリスト。重複なし
            ns_words: 非旬ツイートに含まれていた語がkeyでその出現数がvalue
            """

            sw_count = collections.Counter(words) # season_wordの出現回数のカウントをした。
            s = len(s_twis)
            ns = len(ns_twis)
            N = s + ns

            """
            sw_count: 旬ツイートの語がkeyで、出現回数がvalue
            s: 旬ツイートの数
            ns: 非旬ツイートの数
            N: ツイート総数
            """

            pmi_of_word = {}
            for w, c in sw_count.items():
                if w in keywords[flag]:
                    continue
                sw = c
                ns_w = ns_words[w] if w in ns_words else 0
                wc = sw + ns_w
                if not any([wc < 1, s < 1]):
                    pmi_of_word[w] = calc_pmi(sw, wc, s, N)
            sorted_pmi = sorted(pmi_of_word.items(), key=lambda x:x[1], reverse=True)

            """
            ※対象語の場合は処理しない
            sw: ある語の旬ツイートでの出現回数。
            ns_w: ある語の非旬ツイートでの出現回数。
            wc: ある語の全ツイートでの出現回数。
            sorted_pmi: keyが語、valueがそのpmiの辞書。pmiが大きい順
            """

            soa_of_word = {}
            for w, c in sw_count.items():
                if w in keywords[flag]:
                    continue
                sw = c
                ns_w = ns_words[w] if w in ns_words else 0
                wc = sw + ns_w
                if not any([wc < 1, s < 1, ns < 1]):
                    soa_of_word[w] = calc_soa(sw, ns_w, wc, s, ns, N)
            sorted_soa = sorted(soa_of_word.items(), key=lambda x:x[1], reverse=True)

            result_dir = '/now24/naruse/out/2014/'

            os.makedirs(result_dir + 'pmi/', exist_ok=True)
            with open(result_dir + 'pmi/' + pref + '_' + flag + '_pmi.txt', 'w') as f:
                for w, pmi in sorted_pmi:
                    f.write(f'{w}, {pmi}\n')
            os.makedirs(result_dir + 'soa/', exist_ok=True)
            with open(result_dir + 'soa/' + pref + '_' + flag + '_soa.txt', 'w') as f:
                for w, soa in sorted_soa:
                    f.write(f'{w}, {soa}\n')

main()
