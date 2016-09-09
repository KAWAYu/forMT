"""
tedから2言語間で対応しているtalkidの
タイトル(title)、概要(description)、内容をとりだします

使い方(Usage):
python from_ted2str.py input_file1 input_file2 output_file1 output_file2
    input_file1 ... tedのxmlファイル
    input_file2 ... tedのxmlファイル
    output_file1 ... input_file1から抽出したトランスクリプト
    output_file2 ... input_file2から抽出したトランスクリプト
"""

# encoding: utf-8

import sys

class EngXml:
  # talkid, title, description, seekvideoを格納するクラス
  # talkid: tedのidを格納する。言語間での相違を吸収するため
  # title: tedのタイトルを格納
  # description: talkの概要を格納
  # seekvideo: 内容を格納。リストで保存
  def __init__(self):
    self.talkid = None
    self.title = None
    self.description = None
    self.seekvideo = []

  def set_talkid(self, str): self.talkid = str
  def get_talkid(self): return self.talkid
  def set_title(self, str): self.title = str
  def get_title(self): return self.title
  def set_description(self, str): self.description = str
  def get_description(self): return self.description
  def set_seekvideo(self, str): self.seekvideo.append(str)
  def get_seekvideo(self): return self.seekvideo

def search_talkid(exmlist, searchid):
  """
  exmlistの中でsearchidとtalkidが一致するものを返します

  引数:
    exmlist: EngXmlクラスのリスト
    searchid: 探したいtalkid
  """
  for exml in exmlist:
    if exml.get_talkid() == searchid:
      return exml
  return None

def main():
  # 英語のted
  fen = open(sys.argv[1], "r")
  fileflag = False
  exmlist = []
  talkidflag = False
  tmp_str = []
  # fenファイルのtedの内容をとりあえず全て記録
  for line in fen:
    sent = line.strip()
    if sent.startswith("<file "):
      # 新しいfile内容でexmを更新
      exm = EngXml()
      fileflag = True
    if fileflag:
      # fileタグの中に入っているなら
      if sent.startswith("<talkid>"):
        # taldidをセット
        exm.set_talkid(sent[8:-9])
      elif sent.startswith("<title>"):
        # titleをセット
        exm.set_title(sent[7:-8])
      elif sent.startswith("<description>"):
        # descriptionをセット
        exm.set_description(sent[48:-14])
      elif sent.startswith("<seekvideo "):
        # seekvideoをセット
        exm.set_seekvideo(sent[sent.index('>')+1:-12])
      elif sent.startswith("</file>"):
        exmlist.append(exm)
        fileflag = False
  fen.close()

  fja = open(sys.argv[2], "r")
  fenout = open(sys.argv[3], "w")
  fjaout = open(sys.argv[4], "w")
  for line in fja:
    sent = line.strip()
    if sent.startswith("<file "):
      # 新しいfile内容
      fileflag = True
    if fileflag:
      if sent.startswith("<talkid>"):
        id = sent[8:-9]
        exm = search_talkid(exmlist, id)
        if exm != None:
          # 両方に同じtalkidを持つtedtalkが見つかったら
          talkidflag = True
      if talkidflag:
        if sent.startswith("<title>"):
          print(sent[7:-8], file=fjaout)
          print(exm.get_title(), file=fenout)
        elif sent.startswith("<description"):
          print(sent[48:-14], file=fjaout)
          print(exm.get_description(), file=fenout)
        elif sent.startswith("<seekvideo "):
          tmp_str.append(sent[sent.index('>')+1:-12])
        elif sent.startswith("</file>"):
          for str in exm.get_seekvideo():
            print(str, file=fenout)
          for str in tmp_str:
            print(str, file=fjaout)
          tmp_str.clear()
          fileflag = False
          talkidflag = False
  fja.close()

if __name__=="__main__":
  main()