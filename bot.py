import discord
from discord import app_commands
from discord.ext import commands
import json
import os
from datetime import datetime

# =========================
# 設定
# =========================

TOKEN = os.getenv("DISCORD_TOKEN")

# 固定対象のユーザーID
TARGET_USER_ID = 393001269746335745

# 表示名（好きに変えてOK）
TARGET_NAME = "ハヤ様"

DATA_FILE = "betray_data.json"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


# =========================
# データ読み書き
# =========================

def load_data():
    if not os.path.exists(DATA_FILE):
        return {
            "count": 0,
            "history": []
        }

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# =========================
# 起動時
# =========================

@bot.event
async def on_ready():
    print(f"ログイン完了: {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"コマンド同期完了: {len(synced)}個")
    except Exception as e:
        print(e)


# =========================
# /裏切り追加
# =========================

@bot.tree.command(name="裏切り追加", description="裏切り回数を追加します")
@app_commands.describe(
    reason="裏切りの理由"
)
async def betray_add(
    interaction: discord.Interaction,
    reason: str
):
    data = load_data()

    data["count"] += 1

    history_entry = {
        "reason": reason,
        "reporter": interaction.user.display_name,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    data["history"].append(history_entry)

    save_data(data)

    await interaction.response.send_message(
        f"⚠ 裏切り検知 ⚠\n\n"
        f"{TARGET_NAME} の裏切り回数が増加しました。\n"
        f"現在：**{data['count']} betray**\n\n"
        f"最新の罪：\n"
        f"「{reason}」\n\n"
        f"告発者：{interaction.user.mention}"
    )


# =========================
# /裏切り確認
# =========================

@bot.tree.command(name="裏切り確認", description="裏切り回数を確認します")
async def betray_check(interaction: discord.Interaction):
    data = load_data()

    history = data["history"][-5:]  # 最新5件

    history_text = ""

    if history:
        for i, item in enumerate(reversed(history), 1):
            history_text += (
                f"{i}. {item['reason']}\n"
                f"　告発者：{item['reporter']}\n"
                f"　日時：{item['date']}\n\n"
            )
    else:
        history_text = "履歴なし"

    await interaction.response.send_message(
        f"⚠ 裏切り記録照会 ⚠\n\n"
        f"{TARGET_NAME} の現在の裏切り回数："
        f"**{data['count']} betray**\n\n"
        f"最近の罪：\n\n{history_text}"
    )


# =========================
# 起動
# =========================

bot.run(TOKEN)