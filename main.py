from threading import Thread
from replit import db
from colors import *
import requests
import discord
import time
import os

client = discord.Client()
guilds = {}
friends = []

# send message using Discord REST API
def send_message(channel_id, text: str):
  headers = {'authorization': os.environ['AUTH_TOKEN_MAIN'], 'content-type': 'application/json'}
  json = {'content': text}
  requests.post(f'https://discord.com/api/v9/channels/{channel_id}/messages', headers=headers, json=json)

# gets list of discord servers using Discord REST API
def get_all_servers():
  headers = {'authorization': os.environ['AUTH_TOKEN_MAIN'], 'content-type': 'application/json'}
  request = requests.get('https://discordapp.com/api/users/@me/guilds', headers=headers)
  servers = []
  for server in request.json():
    servers.append({'name': server['name'], 'id': server['id']})
  return servers

# sends messages to Discord 
def message_sender():
  global channel_id, ready, listening
  if not listening == '':
    # time delay for channel query
    time.sleep(4)
    channel_id = input('Select a channel ID to send messages to: ')
    os.system('clear')

    print_history(channel_id)
  # set ready
  ready = True
  while True:
    message = input()
    # change which server is being listened to
    if message == '--server':
      # remove ready
      ready = False
      
      os.system('clear')
      servers = get_all_servers()
      for server in servers:
        print(f'[{blue}{server["name"]}{white}] || {server["id"]}')
      server_id = input('Select a server ID to view and send messages in: ')
      listening = int(server_id) if not server_id == '' else ''
      os.system('clear')

      if not listening == '':
        for channel in guilds[listening]:
          print(f'[{blue}{channel["name"]}{white}] || {channel["id"]}')
        channel_id = input('Select a channel ID to send messages to: ')
        os.system('clear')
        print_history(channel_id)

        # set ready
      ready = True

    # changes which channel is being listened to
    elif message == '--channel':
      # remove ready
      ready = False
      
      os.system('clear')
      if not listening == '':
        for channel in guilds[listening]:
          print(f'[{blue}{channel["name"]}{white}] || {channel["id"]}')
        channel_id = input('Select a channel ID to send messages to: ')
        os.system('clear')
        print_history(channel_id)

        # set ready
        ready = True
    elif message == '--clear':
      os.system('clear')
    elif message == '--friends':
      ready = False
      os.system('clear')
      for friend in friends:
        print(f'{bright_blue}{friend}{white}')
      input()
      os.system('clear')
      ready = True
    else:
      # send regular message
      print('\033[1A' + '\033[K', end='')
      send_message(channel_id, message)

# print message history
def print_history(channel, limit=10):
  headers = {'authorization': os.environ['AUTH_TOKEN_MAIN'], 'content-type': 'application/json'}
  request = requests.get(f'https://discord.com/api/v9/channels/{channel}/messages?limit={limit}', headers=headers)
  items = request.json()
  for index, item in enumerate(items):
    print(f'[{bright_blue}{items[limit-index-1]["author"]["username"]}#{items[limit-index-1]["author"]["discriminator"]}{white}] || {items[limit-index-1]["content"]}')

@client.event
async def on_ready():  
  global listening, ready
  # get friends
  for friend in client.user.friends:
    friends.append(friend)
  # query channels
  for server in client.guilds:
    guilds[server.id] = []
    for channel in server.channels:
      if str(channel.type) == 'text':
        guilds[server.id].append({'name': channel.name, 'id': channel.id})

  try:
    # except no selected server
    for channel in guilds[listening]:
      print(f'[{blue}{channel["name"]}{white}] || {channel["id"]}')
  except KeyError: pass

  # only prints debug information when ready
  while not ready is True: pass
  print('\n'+str(client.user))
  print(f'ping: {round(client.latency, 3)} ms\n')

@client.event
async def on_message(message):
  global listening, ready
  # checks if message is a bot message to avoid spam
  if message.author.bot is False and ready is True:
    if listening == '' or listening == message.guild.id:
      # getting message by bypassing intents
      async for message in message.channel.history(limit=1): 
        msg = str(message.content)
        print(f'[{blue}{message.guild.name}{white}] {bright_blue}{str(message.author)} {white}in {bright_blue}{client.get_channel(message.channel.id)} {white}|| {msg}')
      
if __name__ == '__main__':
  os.system('clear')
  
  # prompt
  servers = get_all_servers()
  for server in servers:
    print(f'[{blue}{server["name"]}{white}] || {server["id"]}')
  server_id = input('Select a server ID to view and send messages in: ')
  os.system('clear')
  # check for selected server
  listening = int(server_id) if not server_id == '' else ''
  channel_id = ''

  # set ready
  ready = False
  Thread(target=message_sender).start()
  client.run(os.environ['TOKEN_MAIN'], bot=False)
