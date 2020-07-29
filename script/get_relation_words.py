"""
教師データのツイート内に含まれる各単語と
"イチョウ"の関連度を計算する
"""

from s_lib import setup_mongo
import sys, math, collections

icho = ["いちょう", "イチョウ", "銀杏"]
kaede = ["かえで", "カエデ", "楓"]
sonota = ["こうよう", "もみじ", "紅葉", "黄葉", "コウヨウ", "モミジ"]
koyo = icho + kaede + sonota

def daterange(_start, _end):
    for n in range((_end - _start + timedelta(days=1)).days):
        yield _start + timedelta(n)

def calc_pmi(sw, w, s, N):
  pmi = math.log2(((sw + 1) * N) / (w * s))
  return(pmi)

def calc_soa(sw, ns_w, w, s, ns, N):
    #  soa = math.log2(((sw + 1) * ns)/((ns_w + 1) * s))
    soa = calc_pmi(sw, w, s, N) - calc_pmi(ns_w, w, ns, N)
    return(soa)

def main():
    args = sys.argv

    db = setup_mongo('2014_twi')
    pname = ["hk"] # ["tk", "hk", "is"]

    start = datetime.strptime('2014-10-30', '%Y-%m-%d')
    end = datetime.strptime('2014-11-03', '%Y-%m-%d')

    correct_duration = daterange(start, end)

    col = db["2014" + month + pname]

    s_twis = list(col.find({'koyo': 1}))
    ns_twis = list(col.find({'koyo': 0}))

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

    sw_count = collections.Counter(words) # season_wordのカウントをした。
    s = len(s_twis)
    ns = len(ns_twis)
    N = s + ns

    pmi_of_word = {}
    for w, c in sw_count.items():
        if w in keywords:
            continue
        sw = c
        ns_w = ns_words[w] if w in ns_words else 0
        wc = sw + ns_w
        if not any([wc < 1, s < 1]):
            pmi_of_word[w] = calc_pmi(sw, wc, s, N)
    sorted_pmi = sorted(pmi_of_word.items(), key=lambda x:x[1], reverse=True)

    with open('/now24/naruse/tmp/' + pname + '_pmi.txt', 'w') as f:
        for w, pmi in sorted_pmi:
            f.write(f'{w}, {pmi}\n')

    soa_of_word = {}
    for w, c in sw_count.items():
        if w in keywords:
            continue
        sw = c
        ns_w = ns_words[w] if w in ns_words else 0
        wc = sw + ns_w
        if not s < 1:
            soa_of_word[w] = calc_soa(sw, ns_w, wc, s, ns, N)
    sorted_soa = sorted(soa_of_word.items(), key=lambda x:x[1], reverse=True)
    with open('/now24/naruse/tmp/' + pname + '_soa.txt', 'w') as f:
        for w, soa in sorted_soa:
            f.write(f'{w}, {soa}\n')


main()
