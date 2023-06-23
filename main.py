import discord
from discord.ext import commands, tasks
# from cogs.RevvingCheckCog import RevvingCheckCog
from discord import app_commands    
import json
from web3 import Web3
import os
import asyncio
import pandas as pd
class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        # intents.messages  = True
        intents.message_content = True
        super().__init__(command_prefix="/",intents=intents)
        self.initial_extensions = [
#             'cogs.RevvingCheckCog'
        ]

    async def setup_hook(self):
        for ext in self.initial_extensions:
            await self.load_extension(ext)

    async def close(self):
        await super().close()

    async def on_ready(self):
        await self.tree.sync()
        print('Ready!')

with open('credentials.json', 'r', encoding='utf-8') as f:
    CREDENTIALS = json.loads(f.read())
TOKEN = CREDENTIALS["token"]

with open('contract_abi.json', 'r', encoding='utf-8') as f:
    ABI = json.loads(f.read())
COLLECTION_ABI = ABI["result"]
COLLECTION_ADDRESS = '0xf10a5f9feef5b3c52c7ca71dc11e467b727c7222'
COLLECTION_ADDRESS = Web3.to_checksum_address(COLLECTION_ADDRESS)
# Discord bot token
TOKEN = CREDENTIALS["token"]
KEY = CREDENTIALS["infura_key"]
# Target Discord channel
TARGET_CHANNEL_ID = 1061678285920149554

# Ethereum provider URL
PROVIDER_URL = f"https://mainnet.infura.io/v3/{KEY}"
web3 = Web3(Web3.HTTPProvider(PROVIDER_URL))

collection = web3.eth.contract(address=COLLECTION_ADDRESS, abi=COLLECTION_ABI)

with open('metadata.txt', 'r') as f:
    metadata = f.readlines()
metadata = eval(metadata[0])
meta_all = pd.DataFrame(metadata)
meta_small = pd.DataFrame(metadata).loc[:, ["id", "tribe"]]
bot = MyBot()


@bot.tree.command(name="query", description="check the revving status of specific token id")
async def self(interaction:discord.Interaction, token_id: int):
    
    image_url = f'https://www.bosotokyo.com/gallery_images_webp_grid/{token_id}.webp'
    title = f'BŌSŌ TOKYO #{token_id}'
    url = f'https://opensea.io/assets/ethereum/0xf10a5f9feef5b3c52c7ca71dc11e467b727c7222/{token_id}'
    Revving_info = collection.functions.revvingPeriod(token_id).__call__(token_id).call()
    tribe = meta_small.loc[meta_small.loc[:,"id"]==str(token_id)]["tribe"].values[0]
    RPM_time = Revving_info[2]
    if Revving_info[0]==True:
        description = "Revvving :white_check_mark:\n"
        description += "If you want to purchase this BOSO, please request in #🔐|un-revving-request\n"
    else:
        description = "Not revving :x:\n"
    if tribe == "Chimera":
        RPM = RPM_time//600
    elif tribe == "Machine":
        RPM = RPM_time//570
    else:
        RPM = RPM_time//540
    description += f"Total RPM: {RPM}"
    embed = discord.Embed(
            colour=discord.Colour.dark_teal(),
            title=title,
            url=url,
            description=description
        )
#     embed.set_footer(text="this is the footer")
#     embed.set_author(name="Richard", url="https://www.youtube.com/channel/UCIJe3dIHGq1lIAxCCwx8eyA")

#     embed.set_thumbnail(url="https://yt3.ggpht.com/GiBCvnzO8e3_cPclwtRCUqLye86F0_xNOPK0FYeshaths5DO2SLvJq9cBVZ0BL-oNwjt90huIw=s108-c-k-c0x00ffffff-no-rj")
    embed.set_image(url=image_url)

#     embed.add_field(name="Website", value="richardschwabe.de")

    await interaction.response.send_message(embed=embed)
    
#     if channel.permissions_for(interaction.user).administrator:
#         config = {}
#         with open(os.path.abspath('config.json'), 'r') as f:
#             config = json.loads(f.read())
#         if config.get(str(channel.guild.id)):
#             config[str(channel.guild.id)]["read_channel_id_JP"] = channel.id
#         else:
#             config[str(channel.guild.id)] = {}
#             config[str(channel.guild.id)]["read_channel_id_JP"] = channel.id
#         with open(os.path.abspath('config.json'), "w") as outfile:
#             json.dumps(config, outfile) 
#         await interaction.response.send_message(f"Start reading JP channel <#{channel.id}>")
#     else:
#         await interaction.response.send_message("Sorry, you have no permission to use this command")

bot.run(TOKEN)


# @bot.event
# async def on_ready():
#     print(f"Logged in as {bot.user.name}")
# async def main():
#     async with bot:
# #         await bot.load_extensions("cogs.RevvingCheckCog")
#         await bot.start(TOKEN)

# asyncio.run(main())