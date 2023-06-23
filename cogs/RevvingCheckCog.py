import discord
from discord.ext import commands
from discord import Client
import requests
import json
import googletrans



import os

with open(os.path.abspath('credentials.json'), 'r', encoding='utf-8') as f:
    CREDENTIALS = json.loads(f.read())
DEEPL_API_KEY = CREDENTIALS["DeepLApi"]
last_speaker = ""
PARAMS = {
    "last_speaker":last_speaker
}
def get_translation(text, target_lang="en"):
    headers = {
        'Authorization': f'DeepL-Auth-Key {DEEPL_API_KEY}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'text': text,
        'target_lang': target_lang
    }
    response = requests.post('https://api-free.deepl.com/v2/translate', headers=headers, data=data)
    if response.status_code  == 4002:
        return 4002
    result = json.loads(response.text)
    return result['translations'][0]['text']
class RevvingCheckCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open(os.path.abspath('config.json'), 'r') as f:
            self.config = json.loads(f.read())
     
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        Name = message.author.display_name
        Avatar = message.author.display_avatar.url
        guild_id = message.channel.guild.id
        message_channel = message.channel.id
        text = message.content
        attachments = message.attachments
            
        if self.config.get(str(guild_id)):
            All_set = 0
            if self.config[str(guild_id)].get("read_channel_id_JP"):
                read_channel_id_JP = self.config[str(guild_id)]["read_channel_id_JP"]
                All_set += 1
            if self.config[str(guild_id)].get("read_channel_id_other"):
                read_channel_id_other = self.config[str(guild_id)]["read_channel_id_other"]
                All_set += 1
            if self.config[str(guild_id)].get("reply_channel_id_EN"):
                reply_channel_id_EN = self.config[str(guild_id)]["reply_channel_id_EN"]
                All_set += 1
            if self.config[str(guild_id)].get("reply_channel_id_CN"):
                reply_channel_id_EN = self.config[str(guild_id)]["reply_channel_id_CN"]
                All_set += 1

            if All_set != 4:
                return


        if message_channel in [read_channel_id_JP]:
            target_channel_EN = self.bot.get_channel(reply_channel_id_EN)
            target_channel_CN = self.bot.get_channel(reply_channel_id_CN)
            translated_text_EN = get_translation(text, target_lang="en")
            # Note the target lang is zh not cn
            translated_text_CN = get_translation(text, target_lang="zh")
            
            # send JP -> EN message to English channel
            webhook = await target_channel_EN.create_webhook(name=Name)
            if text != "":
                await webhook.send(
                    str(translated_text_EN), username=Name, avatar_url=Avatar)

            if len(attachments) !=0:
                for attachment in attachments:
                    await webhook.send(
                        attachment.url, username=Name, avatar_url=Avatar)
            # send JP -> CN message to English channel
            webhook = await target_channel_CN.create_webhook(name=Name)
            if text != "":
                await webhook.send(
                    str(translated_text_CN), username=Name, avatar_url=Avatar)

            if len(attachments) !=0:
                for attachment in attachments:
                    await webhook.send(
                        attachment.url, username=Name, avatar_url=Avatar)
            webhooks = await target_channel_EN.webhooks()
            for webhook in webhooks:
                await webhook.delete()
            webhooks = await target_channel_CN.webhooks()
            for webhook in webhooks:
                await webhook.delete()
            
        elif message_channel in read_channel_id_other:
            target_channel_JP = self.bot.get_channel(reply_channel_id_EN)
            translated_text = get_translation(text, target_lang="ja")

            webhook = await target_channel_JP.create_webhook(name=Name)
            if text != "":
                await webhook.send(
                    str(translated_text), username=Name, avatar_url=Avatar)

            if len(attachments) !=0:
                for attachment in attachments:
                    await webhook.send(
                        attachment.url, username=Name, avatar_url=Avatar)
            webhooks = await target_channel_JP.webhooks()
            for webhook in webhooks:
                await webhook.delete()
            
        else:
            return
 
 
        # webhook = await target_channel.create_webhook(name=Name)
        # if text != "":
        #     await webhook.send(
        #         str(translated_text), username=Name, avatar_url=Avatar)

        # if len(attachments) !=0:
        #     for attachment in attachments:
        #         await webhook.send(
        #             attachment.url, username=Name, avatar_url=Avatar)
        # webhooks = await target_channel.webhooks()
        # for webhook in webhooks:
        #     await webhook.delete()
        # webhooks = await target_channel_EN.webhooks()
        # for webhook in webhooks:
        #     await webhook.delete()
        # webhooks = await target_channel.webhooks()
        # for webhook in webhooks:
        #     await webhook.delete()




    # @commands.command()
    # async def set_read_channel(self, ctx, read_channel: discord.TextChannel):
    #     if ctx.channel.permissions_for(ctx.author).administrator:
    #         if config.get(str(channel.guild.id)):
    #             config[str(channel.guild.id)]["read_channel_id"] = read_channel.id
    #         else:
    #             config[str(channel.guild.id)] = {}
    #             config[str(channel.guild.id)]["read_channel_id"] = read_channel.id
    #         with open(os.path.abspath('config.json'), "w") as outfile:
    #             json.dump(config, outfile) 
    #         await ctx.send(f"Start reading channel <#{read_channel.id}>")
    #     else:
    #         await ctx.send("Sorry, you have no permission to use this command")
        
    @commands.command()
    async def set_reply_channel(self, ctx, reply_channel: discord.TextChannel):
        if ctx.channel.permissions_for(ctx.author).administrator:
            if config.get(str(channel.guild.id)):
                config[str(channel.guild.id)]["reply_channel_id"] = reply_channel.id
            else:
                config[str(channel.guild.id)] = {}
                config[str(channel.guild.id)]["reply_channel_id"] = reply_channel.id
            with open(os.path.abspath('config.json'), "w") as outfile:
                json.dump(config, outfile) 
            await ctx.send(f"Replying to channel <#{reply_channel.id}>")
        else:
            await ctx.send("Sorry, you have no permission to use this command")

async def setup(bot):
    await bot.add_cog(TranslateCog(bot))