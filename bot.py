import discord
from discord import app_commands
import os
from supabase import create_client, Client
from flask import Flask
import threading

# ========================
# 環境変数
# ========================
TOKEN = os.environ.get("DISCORD_TOKEN")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

TARGET_NAME = "対象者"  # 好きに変えてOK

# ========================
# Supabase
# ========================
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ========================
# Discord設定
# ========================
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# ========================
# 起動時
# ========================
@client.event
async def on_ready():
    await tree.sync()
    print("ログイン完了")

# ========================
# コマンド
# ========================
@tree.command(name="裏切り追加", description="裏切り回数を追加します")
@app_commands.describe(reason="裏切りの理由")
async def betray_add(interaction: discord.Interaction, reason: str):
    # 先に応答（これが超重要）
    await interaction.response.defer()

    try:
        # DB保存
        supabase.table("betray_logs").insert({
            "reason": reason,
            "reporter": interaction.user.display_name
        }).execute()

        # 件数取得
        result = supabase.table("betray_logs").select("id").execute()
        count = len(result.data)

        # 返信
        await interaction.followup.send(
            f"⚠ 裏切り検知 ⚠\n\n"
            f"{TARGET_NAME} の裏切り回数が増加しました。\n"
            f"現在：**{count} betray**\n\n"
            f"最新の罪：\n"
            f"「{reason}」\n\n"
            f"告発者：{interaction.user.mention}"
        )

    except Exception as e:
        print("エラー:", e)

        await interaction.followup.send(
            "エラーが発生しました（Supabaseか環境変数の可能性あり）"
        )

# ========================
# Render対策（重要）
# ========================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive"

def run_web():
    app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run_web).start()

# ========================
# 起動
# ========================
client.run(TOKEN)
