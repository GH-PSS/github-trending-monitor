import requests
import xml.etree.ElementTree as ET
import pandas as pd
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
    
    # 記事本文を取得
    try:
        article_response = requests.get(link, timeout=5)
        article_soup = BeautifulSoup(article_response.text, "html.parser")
        paragraphs = article_soup.find_all("p")
        body = "\n".join([p.get_text() for p in paragraphs[:5]])
    except:
        body = "本文取得失敗"
    
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
response = requests.post(WEBHOOK_URL, json=message)
if response.status_code == 204:
    print("Discord通知 成功")
else:
    print(f"失敗: {response.status_code}")

# ⑤ テキストファイル保存（オフライン読書用）
with open("bbc_news.txt", "w", encoding="utf-8") as f:
    for row in data:
        f.write(f"{row['タイトル']}\n{row['URL']}\n\n")
print("テキスト保存完了")
