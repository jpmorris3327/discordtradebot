import discord
import asyncio
import requests
from bs4 import BeautifulSoup
import json
import os





command_prefix = "!"
token = str(os.environ.get("BOT_TOKEN"))

watchlist_channel_ids = [str(os.environ.get("WATCHLIST_CHANNEL_ID"))]
welcome_role_id = str(os.environ.get("WELCOME_ROLE_ID"))
welcome_channel_id = str(os.environ.get("WELCOME_CHANNEL_ID"))
welcome_message = str(os.environ.get("WELCOME_MESSAGE"))

points_enabled = True
points_filename = "points.txt"
admin_role_ids = [str(os.environ.get("ADMIN_ROLE_ID_ONE")), str(os.environ.get("ADMIN_ROLE_ID_TWO"))]
points_role_ids = {
    10: "598362352076718102",
    25: "598364202377412619",
    50: "598364552299544576",
    100: "598364658331549696",
    150: "598364823343857686",
    200: "593972583473348608"
}



invisible_char = "‌‌ "
self_id = str(os.environ.get("SELF_ID"))
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"}
proxies = { 
  "http"  : "http://138.68.240.218:8080", 
  "https" : "https://170.79.16.19:8080"
}
points_dict = {
"330813369898762240": 2, 
"393228932821811210": 11, 
"575977876978139148": 2,
"438676155894333440": 4, 
"597849195688362014": 1, 
"565593383364460555": 3, 
"520358867733970983": 1
}







bot = discord.Client()







try:
    filehandle = open(points_filename, "r")
    points_dict = json.load(filehandle)
except FileNotFoundError:
    filehandle = open(points_filename, "w")
    json.dump(points_dict, filehandle)
filehandle.close()







def get_full_username(user_object):
    return "{0}#{1}".format(user_object.name, user_object.discriminator)






@bot.event
async def on_ready():
    await bot.wait_until_ready()
    print (bot.user.name + " is ready")
    print ("ID: " + bot.user.id)







@bot.event
async def on_member_join(member_object):
    welcome_channel = member_object.server.get_channel(welcome_channel_id)
    await bot.send_message(welcome_channel, welcome_message.format(server=member_object.server.name, member=member_object.mention))

    for role in member_object.server.roles:
        if role.id == welcome_role_id:
            role_object = role
            break
    await bot.add_roles(member_object, role_object)







@bot.event
async def on_message(message_object):
    if message_object.author.id != bot.user.id:

        if message_object.content.lower().startswith(command_prefix):
            command_args = message_object.content[len(command_prefix):].split(" ")
            command_args[0] = command_args[0].lower()







        if command_args[0] == "watch":
            stock_quote = command_args[1].lower()

            link = f"https://www.nasdaq.com/es/symbol/{stock_quote}/real-time"

            response = requests.get(link, headers=headers, proxies=proxies)
            print(response.status_code)
            if not response.status_code in [204, 200]:
                return False
            soup = BeautifulSoup(response.text, features="lxml")

            stock_price = soup.find("div", {"id": "qwidget_lastsale"}).getText()
            stock_change = soup.find("div", {"id": "qwidget_netchange"}).getText()
            stock_percentage = soup.find("div", {"id": "qwidget_percent"}).getText()
            stock_arrow_classes = soup.find("div", {"id": "qwidget-arrow"}).find("div")["class"]

            if "arrow-red" in stock_arrow_classes:
                embed_color = 0xff0000
                stock_change = f"-{stock_change}"
            elif "arrow-green" in stock_arrow_classes:
                embed_color = 0x00ff00
                stock_change = f"+{stock_change}"

            embed = discord.Embed(title=f"**{stock_quote.upper()}**{3*invisible_char}{stock_price}{3*invisible_char}{stock_change} ({stock_percentage})", color=embed_color)
            # embed.set_author(name=get_full_username(message_object.author), icon_url=message_object.author.avatar_url)
            embed.set_footer(text=get_full_username(message_object.author))

            watchlist_channels = []
            for channel_id in watchlist_channel_ids:
                watchlist_channels.append(message_object.server.get_channel(channel_id))

            for watchlist_channel in watchlist_channels:
                await bot.send_message(watchlist_channel, embed=embed)







        elif command_args[0] == "chart":
            stock_quote = command_args[1].lower()

            link = f"https://stockcharts.com/h-sc/ui?s={stock_quote}"

            response = requests.get(link, headers=headers, proxies=proxies)
            if not response.status_code in [204, 200]:
                return False
            soup = BeautifulSoup(response.text, features="lxml")

            chart_image_element = soup.find("img", {"id": "chartImg"})
            chart_image_url = "http:" + chart_image_element["src"]

            embed = discord.Embed(title=stock_quote.upper(), color=0x0000ff)
            embed.set_image(url=chart_image_url)
            embed.set_footer(text=get_full_username(message_object.author))

            await bot.send_message(message_object.channel, embed=embed)







        elif command_args[0] == "points" and points_enabled:
            mention = command_args[1]
            member_id = mention[2:-1]

            member_object = message_object.server.get_member(member_id)
            if member_object == None:
                return

            try:
                member_points = points_dict[member_object.id]
            except KeyError:
                member_points = 0

            if member_points == 1:
                embed = discord.Embed(title=f"{member_points} point", color=0x0000ff)
            else:
                embed = discord.Embed(title=f"{member_points} points", color=0x0000ff)
            embed.set_author(name=get_full_username(member_object), icon_url=member_object.avatar_url)
            await bot.send_message(message_object.channel, embed=embed)







        elif command_args[0] == "help":
            help_message = """
__**General Commands**__

`- {0}watch [quote] - stock price
- {0}chart [quote] - chart for a stock
- {0}points [@member] - shows how many points @member has`

__**Admin Commands**__

`- {0}point [@member] - adds a point to @member`
""".format(command_prefix)

            await bot.send_message(message_object.channel, help_message)





        elif command_args[0] == "backup" and message_object.author.id == self_id:
            print(points_dict)
            await bot.send_message(message_object.author, str(points_dict))






        if bool(set(role_object.id for role_object in message_object.author.roles) & set(admin_role_ids)):

            if command_args[0] == "point" and points_enabled:
                mention = command_args[1]
                member_id = mention[2:-1]

                member_object = message_object.server.get_member(member_id)
                if member_object == None:
                    return

                if member_id in points_dict:
                    points_dict[member_id] += 1
                else:
                    points_dict[member_id] = 1

                filehandle = open(points_filename, "w")
                json.dump(points_dict, filehandle)
                filehandle.close()

                if points_dict[member_id] in points_role_ids:
                    for role in message_object.server.roles:
                        if role.id == points_role_ids[points_dict[member_id]]:
                            role_object = role

                    await bot.add_roles(member_object, role_object)








bot.run(token)
