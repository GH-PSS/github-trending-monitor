import requests
from bs4 import BeautifulSoup
import pandas as pd

# ① スクレイピング
url = "https://github.com/trending"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

data = []
repos = soup.find_all("article", class_="Box-row")

for repo in repos:
    name = repo.find("h2").get_text(strip=True)
    
    desc = repo.find("p")
    desc_text = desc.get_text(strip=True) if desc else "説明なし"
    
    lang = repo.find("span", itemprop="programmingLanguage")
    lang_text = lang.get_text(strip=True) if lang else "不明"
    
    stars = repo.find("span", class_="d-inline-block float-sm-right")
    stars_text = stars.get_text(strip=True) if stars else "0 stars today"
    stars_int = int(stars_text.replace(",", "").replace(" stars today", ""))
    
    data.append({
        "リポジトリ名": name,
        "説明": desc_text,
        "言語": lang_text,
        "本日のスター": stars_int
    })

# ② DataFrame変換
df = pd.DataFrame(data)

# ③ Excel保存
df.to_excel("github_trending.xlsx", index=False)
print("Excel保存完了")

# ④ ソート・上位5件
df_sorted = df.sort_values("本日のスター", ascending=False)
df_top5 = df_sorted.head(5)

# ⑤ Discord通知
WEBHOOK_URL = "https://discord.com/api/webhooks/1510747822046056661/bTlGvYVaDw73tdehJMTVCkXvy6c1OU5n0umD2BaVJMZfsL1rlfFj26WW67PSsRf_Vuwt"

message_lines = ["**📈 GitHub Trending 上位5件**\n"]

for _, row in df_top5.iterrows():
    message_lines.append(
        f"⭐ {row['本日のスター']} stars\n"
        f"📦 {row['リポジトリ名']}\n"
        f"📝 {row['説明']}\n"
    )

message = {"content": "\n".join(message_lines)}
response = requests.post(WEBHOOK_URL, json=message)

if response.status_code == 204:
    print("Discord通知 成功")
else:
    print(f"失敗: {response.status_code}")
