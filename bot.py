


from config import token

import discord
import numpy as np
import random
import json




def get_randint(bound):
    return random.randint(1,bound)


def roll_a_dice(bound,explode=True,value=0):
    dice = get_randint(bound)

    value += dice
    if explode & (dice == bound):
        return roll_a_dice(bound,True,value)
    return value

def roll_n_dices(n,bound,explode=True):
    rolls = np.zeros(n)
    for i in range(n):
        rolls[i] = roll_a_dice(bound,explode,0)
    return rolls


def get_sum(rolls):
    sorted_rolls = np.sort(rolls)
    return int(sum(sorted_rolls[-2:]))


def all_cards(cards):
    all_cards = []
    for key in cards.keys():
        all_cards.extend(cards[key])
    return all_cards

file_name = "cards.json"

def store_cards(client):
    cards = client.stored_values["cards"]
    with open(file_name, 'w') as fp:
        json.dump(cards, fp)



def send_card(channel,card_number):
        with open('images/Cartes-' + str(card_number) + '.png', 'rb') as fp:
            f = discord.File(fp)
            return channel.send(file=f)

def get_player_name(message):
    player = str(message.author).split("#")[0]
    return player


def sort_cards(client):
    for player in client.stored_values["cards"]:
        client.stored_values["cards"][player].sort()

client = discord.Client()


client.stored_values = {
        "count" : 0,
        "dice_value" : 8,
        }

with open(file_name) as json_file:
    client.stored_values["cards"] = json.load(json_file)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):

    content = message.content
    start = content.startswith
    dice_value = client.stored_values["dice_value"]
    channel = message.channel
    if message.author == client.user:
        return

    print(get_player_name(message) + ' - ' + str(content))

    if start('$hello'):
        await message.channel.send("Fais pas le malin mon p'tit gars")


    elif start(';help'):
        await channel.send(';bagarre')
        await channel.send(';explode')
        await channel.send(';change_dices $value')
        await channel.send(';exal')
        await channel.send(';pers')
        await channel.send(';patr')
        await channel.send(';drop_card $value')
        await channel.send(';cards')
        await channel.send(';my_cards')
        await channel.send(';get_card $value')
        await channel.send(';play $value')


    elif start(';bagarre'):
        rolls = roll_n_dices(3,dice_value,False)
        stored_dices = client.stored_values["dices"] = rolls
        ace = client.stored_values["ace"] = (rolls == dice_value)
        await message.channel.send(" ".join(map(lambda x : str(int(x)),rolls)))
        await message.channel.send("Total : " + str(get_sum(stored_dices)))
        for i in range(sum(ace)):
            with open('images/boum.jpg', 'rb') as fp:
                f = discord.File(fp)
                await message.channel.send(file=f)

    elif start(';explode'):
        if "ace" in client.stored_values.keys():
            ace = client.stored_values["ace"]
        else:
            ace = [0]
        if sum(ace) == 0:
            await message.channel.send("Fais pas le malin mon p'tit gars")
            return
        
        stored_dices = client.stored_values["dices"]
        exploding_dices = roll_n_dices(sum(ace),dice_value,False)
        stored_dices[ace] += exploding_dices
        ace[ace] &= (exploding_dices == dice_value)
        await message.channel.send(" ".join(map(lambda x : str(int(x)),exploding_dices)) + " (New roll)")
        await message.channel.send(" ".join(map(lambda x : str(int(x)),stored_dices)) + " (Total)") 
        if sum(ace) == 0:
            await message.channel.send("Total : " + str(get_sum(stored_dices)))
        for i in range(sum(ace)):
            with open('images/boum.jpg', 'rb') as fp:
                f = discord.File(fp)
                await message.channel.send(file=f)


    elif start(';test'):
        
        await message.channel.send(message.author)
        await message.channel.send(player_discord_names[str(message.author).split('#')[0]])

    elif start(';change_dices'):
        try:
            dice_value = int(str(content).split(" ")[1])
            client.stored_values["dice_value"] = dice_value
            await message.channel.send("C'est toi le boss")
        except:
            await message.channel.send("Ya un truc qui va pas, format ';change_dice_value 8'")

    elif start(';exal'):
        boule = True
        player = get_player_name(message)
        
        while boule:
            new_card = random.randint(1,54)
            boule = new_card in all_cards(client.stored_values["cards"])
        await message.channel.send("Carte tirée : " + str(new_card))
        client.stored_values["cards"][player].append(new_card)
        store_cards(client)
        await send_card(message.channel,new_card)
        sort_cards(client)


    elif start(';pers'):
        boule = True
        player = get_player_name(message)
        
        while boule:
            new_card = random.randint(1,18)+54
            boule = new_card in all_cards(client.stored_values["cards"])
        await message.channel.send("Carte tirée : " + str(new_card))
        client.stored_values["cards"][player].append(new_card)
        store_cards(client)
        await send_card(message.channel,new_card)
        sort_cards(client)

    elif start(';patr'):
        boule = True
        player = get_player_name(message)
        
        while boule:
            new_card = random.randint(1,36)+72
            boule = new_card in all_cards(client.stored_values["cards"])
        await message.channel.send("Carte tirée : " + str(new_card))
        client.stored_values["cards"][player].append(new_card)
        store_cards(client)
        await send_card(message.channel,new_card)
        sort_cards(client)

    elif start(';drop_card'):
        player = get_player_name(message)
        try:
            card_number = int(str(content).split(" ")[1])
        except:
            await message.channel.send("Me faut un numéro de la carte mon goret")
            return
        cards = client.stored_values["cards"][player]
        card_index = cards.index(card_number)
        try:
            cards.pop(card_index)
            await message.channel.send("Voilà voilà")
        except ValueError:
            await message.channel.send("T'as pas la carte mon chou")
            return
        store_cards(client)
        
    elif start(';play'):
        player = get_player_name(message)
        try:
            card_number = int(str(content).split(" ")[1])
        except:
            await message.channel.send("Me faut un numéro de la carte mon goret")
            return
        cards = client.stored_values["cards"][player]
        try:
            card_index = cards.index(card_number)
            cards.pop(card_index)
        except ValueError:
            await message.channel.send("T'as pas la carte mon chou")
            return
        await send_card(channel,card_number)
        store_cards(client)

    elif start(';cards'):
        for key in client.stored_values["cards"].keys():
            await message.channel.send(key + " " + str(client.stored_values["cards"][key]))

    elif start(';get_card'):
        try:
            card_number = int(str(content).split(" ")[1])
        except:
            await message.channel.send("Me faut un numéro de la carte mon goret")
            return
        await send_card(channel,card_number)

    elif start(';my_cards'):
        if " " in content:
            player = content.split(" ")[1]
        else:
            player = get_player_name(message)
        for card_number in client.stored_values["cards"][player]:
            await send_card(channel,card_number)

client.run(token)
