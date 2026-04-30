import os
import discord
from discord import app_commands
from supabase import create_client

TOKEN = os.getenv("DISCORD_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

TARGET_NAME = "裏切り対象"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    await tree.sync()
    print(f"ログイン完了: {client.user}")


@tree.command(name="裏切り追加", description="裏切り回数を追加します")
@app_commands.describe(reason="裏切りの理由")
async def betray_add(interaction: discord.Interaction, reason: str):
    supabase.table("betray_logs").insert({
        "reason": reason,
        "reporter": interaction.user.display_name
    }).execute()

    result = supabase.table("betray_logs").select("id").execute()
    count = len(result.data)

    await interaction.response.send_message(
        f"⚠ 裏切り検知 ⚠\n\n"
        f"{TARGET_NAME} の裏切り回数が増加しました。\n"
        f"現在：**{count} betray**\n\n"
        f"最新の罪：\n"
        f"「{reason}」\n\n"
        f"告発者：{interaction.user.mention}"
    )


@tree.command(name="裏切り確認", description="裏切り回数を確認します")
async def betray_check(interaction: discord.Interaction):
    result = (
        supabase.table("betray_logs")
        .select("reason, reporter, created_at")
        .order("created_at", desc=True)
        .execute()
    )

    logs = result.data
    count = len(logs)

    recent_logs = logs[:5]

    if recent_logs:
        history_text = ""
        for i, item in enumerate(recent_logs, 1):
            history_text += (
                f"{i}. {item['reason']}\n"
                f"　告発者：{item['reporter']}\n"
                f"　日時：{item['created_at']}\n\n"
            )
    else:
        history_text = "履歴なし"

    await interaction.response.send_message(
        f"⚠ 裏切り記録照会 ⚠\n\n"
        f"{TARGET_NAME} の現在の裏切り回数："
        f"**{count} betray**\n\n"
        f"最近の罪：\n\n{history_text}"
    )
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer

def run_web():
    server = HTTPServer(("0.0.0.0", 10000), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_web).start()

client.run(TOKEN)
