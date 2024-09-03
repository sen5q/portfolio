import os
from google.cloud import vision
import requests
import apikey_books
import MeCab
from collections import Counter
import json



def main():
    image1      = "lib/inputa.jpg"
    image2      = "lib/inputb.jpg"
    isbn        = "lib/isbn.txt"
    words1      = "lib/wordsa.txt"
    words2      = "lib/wordsb.txt"
    bookinfo    = "lib/bookinfo.txt"
    worddiff    = "lib/worddiff.txt"
    result      = "lib/result.txt"
    weightpath  = "lib/weights.json"

    img2text(image1, words1)
    img2text(image2, words2)
    isbn2bookinfo(isbn, bookinfo)
    makeweight(words1, weightpath)
    wdiff(words1, words2, worddiff)
    bookcheck(bookinfo, worddiff, result, weightpath)



def img2text(in_image, in_outputpath):

    # キー設定
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "apikey_vision.json"

    # 画像読み込み
    with open(in_image, 'rb') as image_file:
        content = image_file.read()

    # リクエスト送信
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=content)
    response = client.document_text_detection(image=image)

    # 出力
    with open(in_outputpath, 'w', encoding='utf-8') as output:
        for page in response.full_text_annotation.pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    for word in paragraph.words:
                        text = ''.join(symbol.text for symbol in word.symbols)
                        output.write(text)
                        output.write('\n')



def makeweight(in_words, in_outputpath):
    #頻度辞書を作成
    with open(in_words, 'r', encoding='utf-8') as file:
        words = file.read().strip('{}').split('\n')
        word_frequencies = {}
        for word in words:
            word_frequencies[word] = word_frequencies.get(word, 0) + 1

    #重みづけを作成
    output_data = {}
    for word, frequency in word_frequencies.items():
        if frequency == 1:
            output_data[word] = 10
        elif frequency == 2:
            output_data[word] = 3
        elif frequency == 3:
            output_data[word] = 2

    #出力
    with open(in_outputpath, 'w', encoding='utf-8') as f:
        json_data = json.dumps(output_data, ensure_ascii=False, indent=4)
        f.write(json_data)



def isbn2bookinfo(in_isbn, in_outputpath):
    # ISBNリストの読み込み
    with open(in_isbn, "r") as f:
        isbns = f.read().splitlines()

    #書籍情報の取得
    book_info_list = []
    for isbn in isbns:
        title, authors = getbookinfo(isbn)
        book_info_list.append(f"{title}\t{authors}")

    # 出力
    with open(in_outputpath, "w", encoding="utf-8") as f:
        f.write("\n".join(book_info_list))



# 書籍情報を取得する関数
def getbookinfo(isbn):

    # キー設定
    API_KEY = apikey_books.key

    # リクエスト送信
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}&key={API_KEY}"    
    response = requests.get(url)

    #書籍情報を取得
    if response.status_code == 200:
        data = response.json()
        if "items" in data:
            item = data["items"][0]                     # items を取得
            volume_info = item.get("volumeInfo", {})    # itmes/VolumeInfo を取得
            title = volume_info.get("title", "N/A")                     # タイトルを取得
            authors = " ".join(volume_info.get("authors", ["N/A"]))     # 著者情報を取得
            return title, authors                       # タイトルと著者情報を返す
    return "error", "error"



def wdiff(in_filea, in_fileb, in_outputpath):
    # 読み込み
    with open(in_filea, 'r', encoding='utf-8') as file_a:
        words_a = file_a.read().split()
    with open(in_fileb, 'r', encoding='utf-8') as file_b:
        words_b = file_b.read().split()

    # Counterで単語の出現回数を数える
    counter_a = Counter(words_a)
    counter_b = Counter(words_b)

    # 差分計算
    diff_counter = counter_a - counter_b

    # 出力
    with open(in_outputpath, 'w', encoding='utf-8') as f:
        for word in diff_counter.elements():
            f.write(word + '\n')



def bookcheck(in_bookinfo, in_worddiff, in_outputpath, in_weightpath):

    # 読み込み
    with open(in_weightpath, 'r', encoding='utf-8') as file:
        weightdict = json.load(file)
        # 英数字を小文字に変換
        weightdict = {k.lower(): v for k, v in weightdict.items()}

    with open(in_worddiff, 'r', encoding='utf-8') as worddiff_file:
        # word_diffも小文字に変換
        wdiff = set(word.lower() for word in worddiff_file.read().split())

    m = MeCab.Tagger('-Owakati')
    results = []
    with open(in_bookinfo, 'r', encoding='utf-8') as data_b:
        for line in data_b:
            wakati = m.parse(line).split()
            totalweight = sum(weightdict.get(word.lower(), 1) for word in wakati)
            commonweight = sum(weightdict.get(word.lower(), 1) for word in wakati if word.lower() in wdiff)
            ratio = commonweight / totalweight if totalweight > 0 else 0
            results.append((line.strip(), ratio))

    #出力
    with open(in_outputpath, 'w', encoding='utf-8') as f:
        for line, ratio in results:
            line = line[:40]
            f.write(f'{ratio: 15%}\t{line}\n')



main()