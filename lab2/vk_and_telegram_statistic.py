from bs4 import BeautifulSoup
import codecs
import re
import json
import string
import threading
from threading import Thread
from queue import Queue
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import spacy
import vk_api
from telethon.sync import TelegramClient
import asyncio
import tkinter as tk 
import time


vk_key = ""
tg_id = ""
tg_hash = ""

vk_session = vk_api.VkApi(token=vk_key)
vk_api_instance = vk_session.get_api()

nlp = spacy.load("ru_core_news_sm")


def vk_get_user_id(username):
    try:
        response = vk_api_instance.users.get(user_ids=username)
        user_id = response[0]["id"]
        return user_id

    except Exception as e:
        print(f"error {e}")
        return None


def vk_get_wall(owner_id, count):
      response = vk_api_instance.wall.get(owner_id=owner_id, count=count)
      return response["items"]


def parse_vk(groups, data_queue, num_posts):

    for group_id in groups:
        posts = vk_get_wall(group_id, num_posts)
        for post in posts:
            data_queue.put(post["text"])


async def parse_tg(group_names, data_queue, num_messages):
    api_id = tg_id
    api_hash = tg_hash

    client = TelegramClient(
        "session_name", api_id, api_hash, system_version="4.16.30-vxCUSTOM"
    )
    await client.start()

    for group_name in group_names:
        group_entity = await client.get_input_entity(group_name)

        async for message in client.iter_messages(group_entity, limit=num_messages):
            data_queue.put(message.text)

    await client.disconnect()

lock = threading.Lock()


def preprocess_data(data_queue, preprocessed_data, stop_words):
    while True:
        data = data_queue.get()
        if data is None:
            break

        data = data.lower()
        tokens = word_tokenize(data, language="russian")
        tokens = [
            word
            for word in tokens
            if word not in stop_words
            and not all(
                c in string.punctuation + "–«»—“”"
                "utm_source=telegramoid=-67991642act=a_subscribe_boxhttps//vk.com/widget_community.phpstate=1|подпишись"
                for c in word
            )
        ]

        with lock:
            preprocessed_data.extend(tokens)


def show_data(prefix, textarea, text, stop_words):
  words_and_abbreviations = {}
  words = re.findall(r'\b[а-яё]+\b', text.lower())
  for word in words:
    if (len(word) >= 4) and (len(word) <= 12) and (word not in stop_words): 
      if word in words_and_abbreviations:
        words_and_abbreviations[word] += 1
      else:
        words_and_abbreviations[word] = 1
  
  sorted_words = sorted(words_and_abbreviations.items(), key=lambda item: item[1], reverse=True)
#   textarea.delete(1.0, tk.END)
  textarea.insert(tk.END, f"{prefix} words top:\n")
  for i in range(min(10, len(sorted_words))):
      word, count = sorted_words[i]
      textarea.insert(tk.END, f"{i+1}.")
      textarea.insert(tk.END, f"{word}:{count}, ")
  textarea.insert(tk.END, "\n")
  textarea.insert(tk.END, "\n")
  words_and_abbreviations = {}
  words=[]
  sorted_words=[]


def vk_analyze(num_threads, num_vk_posts, stop_words):
    vk_groups = entry_vk_groups.get().split(", ")
    for i in range(len(vk_groups)):
        if vk_groups[i] == 'bookflow':
            show_data(vk_groups[i], result_text_vk, choice("vk\\vk_bookflow.html", "vk"), stop_words)
        if vk_groups[i] == 'iapanoramaspbu':
            show_data(vk_groups[i], result_text_vk, choice("vk\\vk_iapanoramaspbu.html", "vk"), stop_words)
        if vk_groups[i] == 'lyandpy':
            show_data(vk_groups[i], result_text_vk, choice("vk\\vk_lyandpy.html", "vk"), stop_words)
        if vk_groups[i] == 'oproger':
            show_data(vk_groups[i], result_text_vk, choice("vk\\vk_oproger.html", "vk"), stop_words)
        if vk_groups[i] == 'overhearspbsu':
            show_data(vk_groups[i], result_text_vk, choice("vk\\vk_overhearspbsu.html", "vk"), stop_words)
        if vk_groups[i] == 'proglib':
            show_data(vk_groups[i], result_text_vk, choice("vk\\vk_proglib.html", "vk"), stop_words)
        if vk_groups[i] == 'punkovchanin':
            show_data(vk_groups[i], result_text_vk, choice("vk\\vk_punkovchanin.html", "vk"), stop_words)
        if vk_groups[i] == 'spb1724':
            show_data(vk_groups[i], result_text_vk, choice("vk\\vk_spb1724.html", "vk"), stop_words)
        if vk_groups[i] == 'sspmpu':
            show_data(vk_groups[i], result_text_vk, choice("vk\\vk_sspmpu.html", "vk"), stop_words)
        if vk_groups[i] == 'tproger':
            show_data(vk_groups[i], result_text_vk, choice("vk\\vk_tproger.html", "vk"), stop_words)

    data_queue_vk = Queue()
    preprocessed_data_vk = []

    vk_threads = [
        Thread(target=parse_vk, args=(vk_groups, data_queue_vk, num_vk_posts))
        for _ in range(num_threads)
    ]

    process_thread = Thread(
        target=preprocess_data,
        args=(data_queue_vk, preprocessed_data_vk, stop_words),
    )

    for thread in vk_threads:
        thread.start()

    for thread in vk_threads:
        thread.join()

    process_thread.start()

    for _ in range(num_threads):
        data_queue_vk.put(None)

    process_thread.join()
    


def tg_analyze(num_threads, num_telegram_messages, stop_words):
    telegram_groups = entry_tg_groups.get().split(", ")
    for i in range(len(telegram_groups)):
        if telegram_groups[i] == 'c/2070997529':
            show_data(telegram_groups[i], result_text_telegram, choice("tg\\tg_215.json", "tg"), stop_words)
        if telegram_groups[i] == 'c/4502351041':
            show_data(telegram_groups[i], result_text_telegram, choice("tg\\tg_algs.json", "tg"), stop_words)
        if telegram_groups[i] == 'c/2098343335/1':
            show_data(telegram_groups[i], result_text_telegram, choice("tg\\tg_mainchat.json", "tg"), stop_words)
        if telegram_groups[i] == 'piterach':
            show_data(telegram_groups[i], result_text_telegram, choice("tg\\tg_piterach.json", "tg"), stop_words)
        if telegram_groups[i] == 'spbu1724':
            show_data(telegram_groups[i], result_text_telegram, choice("tg\\tg_spbu1724.json", "tg"), stop_words)
        if telegram_groups[i] == 'moskvae':
            show_data(telegram_groups[i], result_text_telegram, choice("tg\\tg_moskvae.json", "tg"), stop_words)
        if telegram_groups[i] == 'sankt6':
            show_data(telegram_groups[i], result_text_telegram, choice("tg\\tg_sankt6.json", "tg"), stop_words)
        if telegram_groups[i] == 'tproger':
            show_data(telegram_groups[i], result_text_telegram, choice("tg\\tg_tproger.json", "tg"), stop_words)
        if telegram_groups[i] == 'vesti_spb':
            show_data(telegram_groups[i], result_text_telegram, choice("tg\\tg_vesti_spb.json", "tg"), stop_words)
        if telegram_groups[i] == 'vestiru24':
            show_data(telegram_groups[i], result_text_telegram, choice("tg\\tg_vestiru24.json", "tg"), stop_words)
            
    data_queue_telegram = Queue()

    preprocessed_data_telegram = []

    telegram_thread = Thread(
        target=lambda: asyncio.run(
            parse_tg(telegram_groups, data_queue_telegram, num_telegram_messages)
        )
    )

    telegram_thread = telegram_thread
    process_thread = Thread(
        target=preprocess_data,
        args=(data_queue_telegram, preprocessed_data_telegram, stop_words),
    )


    process_thread.start()

    for _ in range(num_threads):
        data_queue_telegram.put(None)

    process_thread.join()
        
def choice(path, flag):
    if flag == 'tg':
        text = extract_text_from_json(path)
    if flag == 'vk':
        fileObj = codecs.open(path, "r", "utf_8_sig" )
        text_vk = fileObj.read()
        fileObj.close()

        soup = BeautifulSoup(text_vk, features="lxml")

        for script in soup(["script", "style"]):
            script.extract()

        text = soup.get_text(strip = " ")
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split())
        text = '\n'.join(chunk for chunk in chunks if chunk)

    return(text)

def extract_text_from_json(file_path):
  try:
    with open(file_path, 'r', encoding='utf-8') as f:
      content = f.read()

    texts = []
    for match in re.findall(r'"text":\s*"([^"]*)"', content):
      if match.strip():
        text = re.sub(r'[^а-яёА-ЯЁ\s]', '', match.strip().replace('"', '').replace('\n', ' '))
        texts.append(text)

    combined_text = ' '.join(texts)
    return combined_text

  except FileNotFoundError:
    print(f"Файл {file_path} не найден.")
    return None
  except json.JSONDecodeError:
    print(f"Ошибка декодирования JSON в файле {file_path}.")
    return None


def main():
    result_text_vk.delete(1.0, tk.END)
    result_text_telegram.delete(1.0, tk.END)
    num_threads = 1
    num_vk_posts = 40
    num_telegram_messages = 40
    stop_words = set(stopwords.words("russian"))

    analyze_threads_vk = [
        Thread(target=vk_analyze, args=(num_threads, num_vk_posts, stop_words)),
    ]
    analyze_threads_tg = (
        Thread(
            target=tg_analyze, args=(num_threads, num_telegram_messages, stop_words)
        ),
    )

    for thread in analyze_threads_vk:
        thread.start()

    for thread in analyze_threads_tg:
        thread.start()


if __name__ == "__main__":

    vk_groups = ["spb1724, proglib, lyandpy"]
    telegram_groups = ["c/2098343335/1, spbu1724, piterach"]

    root = tk.Tk()
    root.title("VK and TG Analyzer")

    analyze_button = tk.Button(root, text="Analyze", command=main)
    analyze_button.pack(pady=10)

    label_vk_groups = tk.Label(root, text="VK Group ids:")
    label_vk_groups.pack()

    entry_vk_groups = tk.Entry(root, width=50)
    entry_vk_groups.pack()
    entry_vk_groups.insert(0, vk_groups)

    result_text_vk = tk.Text(root)
    result_text_vk.pack()

    label_tg_groups = tk.Label(root, text="TG Group names:")
    label_tg_groups.pack()

    entry_tg_groups = tk.Entry(root, width=50)
    entry_tg_groups.pack()
    entry_tg_groups.insert(0, telegram_groups)

    result_text_telegram = tk.Text(root)
    result_text_telegram.pack()

    root.mainloop()
