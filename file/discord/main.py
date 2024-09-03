# -*- coding: utf-8 -*-

import discord
from discord import app_commands
import os
import _token
import certifi
import os

os.environ["SSL_CERT_FILE"] = certifi.where()

intents = discord.Intents.default()
intents.members = True  # メンバーの情報を取得するため
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)



@client.event
async def on_ready():
    print("ログインしました")

    # スラッシュコマンドを同期
    await tree.sync()



@tree.command(name="move", description="ボイスチャンネルAにいるメンバーをボイスチャンネルBに移動します")
@app_commands.describe(a="移動元のボイスチャンネル", b="移動先のボイスチャンネル")
async def move(interaction:discord.Interaction, a:discord.VoiceChannel, b:discord.VoiceChannel):

    if a == b:
        await interaction.response.send_message("移動元と移動先のボイスチャンネルが同じです。")
        return

    members = a.members
    members_moved = 0

    if not members:
        await interaction.response.send_message("移動元のボイスチャンネルにメンバーがいません。")
        return

    for member in members:
        try:
            await member.move_to(b)
            members_moved += 1
        except discord.Forbidden:
            await interaction.response.send_message(f"{member.name}を移動する権限がありません。")
            return
        except discord.HTTPException:
            await interaction.response.send_message(f"{member.name}の移動に失敗しました。")
            return

    await interaction.response.send_message(f"{members_moved}人のメンバーを{b.name}に移動しました。")



@tree.command(name="gather", description="ボイスチャンネルにメンバーを集めます")
@app_commands.describe(a="メンバーを集めるボイスチャンネル")
async def gather(interaction:discord.Interaction, a:discord.VoiceChannel):
    guild = interaction.guild
    members_moved = 0

    for channel in guild.voice_channels:
        if channel == a:
            continue

        members = channel.members
        for member in members:
            try:
                await member.move_to(a)
                members_moved += 1
            except discord.Forbidden:
                await interaction.response.send_message(f"{member.name}を移動する権限がありません。")
                return
            except discord.HTTPException:
                await interaction.response.send_message(f"{member.name}の移動に失敗しました。")
                return

    if members_moved == 0:
        await interaction.response.send_message("移動するメンバーがいません。")
    else:
        await interaction.response.send_message(f"{members_moved}人のメンバーを{a.name}に移動しました。")



# Botを実行する
client.run(_token.token)