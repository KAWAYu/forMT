# encoding : utf-8

from collections import defaultdict
import math
import sys

def ngram(words, n=1, withS=True):
  """
  受け取った文字列sに対してそのngramを返す関数
  
  引数:
    words : 文字列のリスト
    n : ngramのn(デフォルトで1)
    withS : 文末記号を付けるか(デフォルトでTrue)
  
  戻り値:
    ngramのリスト
  """
  ngram=[]  
  # 文末記号を追加
  if withS==True:
    words.append("</s>")
  if n >= len(words):
    return list(words)
  # 0 ~ len(words)-n+1まで
  for i in range(len(words)-n+1):
    ngram.append(words[i:i+n])
  
  return ngram

def BLEU(r, e):
  """
  1文分のBLEU値を計算して値を返す
  引数の文は単語分割済みでないとうまく働きません。

  引数:
    r : 参照訳の文
    e : BLEU値を計測したい文
  
  戻り値:
    eのBLEU値
  """
  # まずリストにそれぞれを分割
  r_list = r.split()
  e_list = e.split()
  limit = len(r_list) if len(r_list)<len(e_list) else len(e_list)
  
  # マッチ数の初期化
  unimatch=1
  bimatch=1
  trimatch=1
  fourmatch=1

  count=0
  c_e1 = ngram(e_list)
  c_r1 = ngram(r_list)
  for e in c_e1:
    if e in c_r1:
      count += 1.
  unimatch = count/len(c_e1)
  if limit >= 2:
    count = 1.
    c_e = ngram(e_list, n=2)
    c_r = ngram(r_list, n=2)
    for e in c_e:
      if e in c_r:
        count += 1.
    bimatch = count / (len(c_e)+1.)
    if limit >= 3:
      count = 1.
      c_e = ngram(e_list, n=3)
      c_r = ngram(r_list, n=3)
      for e in c_e:
        if e in c_r:
          count += 1.
      trimatch = count / (len(c_e)+1.)
      if limit >= 4:
        count = 1.
        c_e = ngram(e_list, n=4)
        c_r = ngram(r_list, n=4)
        for e in c_e:
          if e in c_r:
            count += 1.
        fourmatch = count / (len(c_e)+1.)
  
  # とりあえずの計算
  tmp_bleu = math.pow(unimatch*bimatch*trimatch*fourmatch, 1.0/4)
  
  # brevity penalty計算用に
  pen = math.exp(1 - float(len(c_r1)) / len(c_e1))
  
  bp = pen if pen<1 else 1
  
  return tmp_bleu * bp

if __name__  == '__main__':
  # 第1引数に参照訳、第2引数に評価したい訳
  fr = open(sys.argv[1])
  fe = open(sys.argv[2])
  sum_bleu = 0
  count = 0
  #fr_len = sum(1 for line in fr)
  #fe_len = sum(1 for line in fe)
  #if fr_len!=fe_len:
   # print("Error: the number of sentences are different!!")
  
  print("caluculating BLEU score")
  for r,e in zip(fr, fe):
    sum_bleu += BLEU(r, e)
    count += 1
  
  print("BLEU: %f"%(float(sum_bleu)/count))
