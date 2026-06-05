import requests
import xml.etree.ElementTree as ET
import pandas as pd
from bs4 import BeautifulSoup  
from dotenv import load_dotenv
import os

load_dotenv()
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# ① RSSフィード取得
url = "https://feeds.bbci.co.uk/news/rss.xml"
response = requests.get(url)
root = ET.fromstring(response.content)

# ② 記事を取り出す
data = []
for item in root.findall(".//item"):
    title = item.find("title").text
    link = item.find("link").text
    
    try:
        article_response = requests.get(link, timeout=5)
        article_soup = BeautifulSoup(article_response.text, "html.parser")
        paragraphs = article_soup.find_all("p")
        body = "\n".join([p.get_text() for p in paragraphs[:5]])
    except Exception as e:
        body = f"本文取得失敗: {e}"  
    
    data.append({"タイトル": title, "URL": link, "本文": body})

# ③ DataFrame変換・Excel保存
df = pd.DataFrame(data)
df.to_excel("bbc_news.xlsx", index=False)
print("Excel保存完了")

# ④ 上位5件をDiscord通知
message_lines = ["**📰 BBC News 最新5件**\n"]
for row in data[:5]:
    message_lines.append(
        f"📌 {row['タイトル']}\n"
        f"🔗 {row['URL']}\n"
    )
message = {"content": "\n".join(message_lines)}
result = requests.post(WEBHOOK_URL, json=message)  
if result.status_code == 204:
    print("Discord通知 成功")
else:
    print(f"失敗: {result.status_code}")

# ⑤ テキストファイル保存（本文も格納）
with open("bbc_news.txt", "w", encoding="utf-8") as f:
    for row in data:
        f.write(f"【{row['タイトル']}】\n")
        f.write(f"{row['URL']}\n\n")
        f.write(f"{row['本文']}\n")
        f.write("-" * 60 + "\n\n")
print("テキスト保存完了")

# ⑥ OneDriveへコピー保存
import shutil

onedrive_path = os.path.expanduser("~/OneDrive/bbc_news")
os.makedirs(onedrive_path, exist_ok=True)
shutil.copy("bbc_news.txt", os.path.join(onedrive_path, "bbc_news.txt"))
shutil.copy("bbc_news.xlsx", os.path.join(onedrive_path, "bbc_news.xlsx"))
print("OneDrive保存完了")


