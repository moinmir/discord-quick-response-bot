from pymongo import MongoClient
import discord
import os
import asyncio




# connecting to database
db_string = os.getenv("DB_STRING")
client_db = MongoClient(db_string,authSource='admin')
db = client_db.serverdata.data



# discord event handlers
client = discord.Client()

@client.event
async def on_ready():
	print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
	if message.author == client.user:
		return

	msg = message.content


	if msg.startswith('$setup'):
		if (message.author.guild_permissions.administrator):
			server_id =  message.guild.id
			data = db.find_one({ "server_id": server_id})
			if (data is None):
				await message.channel.send("```Type the name of the roles you want to enable in lowercase. Seperate multiple roles with commas: ```")  
				try:
					res = await client.wait_for("message", check=checkadmin, timeout=300)
					roles = res.content.split(",")
				except asyncio.TimeoutError:
					return await message.channel.send("```Oops! You took too long to respond. Try again```")

				data = {
					"server_id": message.guild.id,
					"roles": roles
				}

				db.insert_one(data)				
				await message.channel.send("```The Quick Response bot has been set on this server successfully!```")

		
	server_data = db.find_one({ "server_id": message.guild.id })
	if (server_data is None):
		return

	if (common_role(server_data["roles"],[y.name.lower() for y in message.author.roles])):

		if msg.startswith('$hello'):
			await message.channel.send('Hello!')
		

		elif msg.startswith("$new"):
			await message.channel.send("```Reply with the shortcut you want to add: ```")  
			try:
				s = await client.wait_for("message", check=check, timeout=300)
			except asyncio.TimeoutError:
				return await message.channel.send("```Oops! You took too long to respond. Try again```")

			await message.channel.send("```Reply with the response to the shortcut: ```")
			try:
				m = await client.wait_for("message", check=check, timeout=300)
			except asyncio.TimeoutError:
				return await message.channel.send("```Oops! You took too long to respond. Try again```")

			response = add_shortcut(s.content, m.content, server_data)
			await message.channel.send(response)


		elif msg.startswith("$del"):
			shortcut = msg.split("$del ",1)[1]
			response = delete_shortcut(shortcut, server_data)
			await message.channel.send(response)


		elif msg.startswith("$remove"):
			server_id =  message.guild.id
			db.delete_one({ "server_id": server_id })
				
			await message.channel.send("```Quick Response bot has been removed from this server successfully!```")


		else:
			response = fetch_shortcut(msg, server_data)
			if (response):
				await message.channel.send(response)




def checkadmin(m):
	server_data = db.find_one({ "server_id": m.guild.id })
	if (m.author.guild_permissions.administrator):
		return m.content

def check(m):
	server_data = db.find_one({ "server_id": m.guild.id })
	if (common_role(server_data["roles"],[y.name.lower() for y in m.author.roles])):
		return m.content


def add_shortcut(s, m, server_data):
	if "shortcut" in server_data.keys():
		shortcut = server_data["shortcut"]
		for i in shortcut:
			if i[0] == s:
				return "```Shortcut already exists in the database.```"
	else:
		shortcut = []
	shortcut.append([s, m])
	db.update_one({ "server_id": server_data["server_id"] }, {'$set': { "shortcut": shortcut }})

		
	return "```Shortcut has been added successfully!```"



def fetch_shortcut(shortcut, server_data):
	if "shortcut" in server_data.keys():
		shortcuts = server_data["shortcut"]
		for i in shortcuts:
			if i[0] == shortcut:
				return i[1]
			
	


def delete_shortcut(shortcut, server_data):
	if "shortcut" in server_data.keys():
		shortcuts = server_data["shortcut"]
		for i in range(0,len(shortcuts)):
			if shortcuts[i][0] in shortcut:
				shortcuts.remove(shortcuts[i])
				db.update_one({ "server_id": server_data["server_id"] }, {'$set': { "shortcut": shortcuts }})
				return "`Shortcut deleted successfully!`"
		return "`Shortcut does not exist`"


def common_role(list1, list2):
    result = False
    # traverse in the 1st list
    for x in list1:
        # traverse in the 2nd list
        for y in list2:
            # if one common
            if x == y:
                result = True
                return result 
    return result
		

token = os.getenv("DISCORD_BOT_TOKEN")
client.run(token)
