from config import token
from config import players
from toolbox import *

import discord
import numpy as np
import random
import json



file_name = "cards.json"
players_json = "players.json"

async def cmd_hello(message):
    """Un p'tit coucou"""
    await message.channel.send("Fais pas le malin mon p'tit gars")

async def cmd_bagarre(message):
    """Faire un jet de dé. Il est possible de préciser le type de jet ;bagarre type (soldat, voyageur, érudit, archer, assassin, berzekr, guerrier)"""
    dice_value = client.stored_values["dice_value"]
    bonus_touch, bonus_dmg, jet = parse_bagarre(message) 
    rolls = roll_n_dices(3,dice_value,False)
    player = get_player_name(message)
    client.stored_values["jets"][player] = jet
    client.stored_values["dices"][player] = rolls
    ace = client.stored_values["ace"][player] = (rolls == dice_value)
    weapon = client.stored_values["players"][player]["weapon"]
    weapon_bonus = client.stored_values["players"][player]["weapon_bonus"]
    msg_bagarre = format_bagarre(player, jet, rolls, bonus_touch, bonus_dmg, weapon, weapon_bonus)
    await message.channel.send(msg_bagarre)
    for i in range(sum(ace)):
        with open('images/boum.jpg', 'rb') as fp:
            f = discord.File(fp)
            await message.channel.send(file=f)

def parse_bagarre(message):
    values = message.content.split()
    player = get_player_name(message)
    jet = None
    if len(values) > 1:
        jet = values[1]
    return get_bonus(jet, player) + (jet,)

def get_bonus(jet, player):
    bonus_touch = 0
    bonus_dmg = 0
    if jet in classes:
        if jet in ["soldat", "voyageur", "érudit"]:
            bonus_touch = client.stored_values["players"][player][jet]
        else:
            bonus_touch = client.stored_values["players"][player]["soldat"]
            if jet == "berzekr":
                bonus_touch += client.stored_values["players"][player]["berzekr"]
                bonus_dmg = client.stored_values["players"][player]["berzekr"]
            elif jet in ["guerrier", "archer"]:
                bonus_dmg = client.stored_values["players"][player][jet]
    return bonus_touch, bonus_dmg

def format_bagarre(player, jet, rolls, bonus_touch, bonus_dmg, weapon=None, weapon_bonus = 0):
    rolls_txt = " ".join(map(lambda x : str(int(x)),rolls))
    mait, prou, exalt = map(lambda x: int(x), rolls)
    if jet:
        msg = "Jet de %s de %s\n" % (jet, player)
    else:
        msg = "Jet standard de %s\n" % player
    if weapon:
        msg += "Arme (les dégâts à appliquer manuellement): %s\n" % weapons_dict[weapon]
        msg += "Bonus arme: + %d dégâts\n" % int(weapon_bonus)
    msg += "Jet: %s (Bonus touche: %d, Bonus dégâts: %d)\n" % (rolls_txt, bonus_touch, bonus_dmg)
    msg += "%d (%d dégâts) ou %d (%d dégâts) ou %d (%d dégâts)" % (
            mait + prou + bonus_touch,
            mait + bonus_dmg,
            mait + exalt + bonus_touch,
            mait + bonus_dmg,
            exalt + prou + bonus_touch,
            exalt + bonus_dmg)
    return msg

async def cmd_skills(message):
    """Affiche les statistiques"""
    player = get_player_name(message)
    msg = "Compétences de %s\n" % player
    msg += "\n".join(["%s: %s" % (key,val) for (key,val) in client.stored_values["players"][player].items()])
    await message.channel.send(msg)

async def cmd_explode(message):
    """Relance les dés qui ont explosé au précédent jet du joueur"""
    player = get_player_name(message)
    dice_value = client.stored_values["dice_value"]
    jet = None
    if player in client.stored_values["ace"].keys():
        jet = client.stored_values["jets"][player]
        ace = client.stored_values["ace"][player]
    else:
        ace = [0]
    if sum(ace) == 0:
        await message.channel.send("Fais pas le malin mon p'tit gars")
        return
    bonus_touch, bonus_dmg = get_bonus(jet, player)
    stored_dices = client.stored_values["dices"][player]
    exploding_dices = roll_n_dices(sum(ace),dice_value,False)
    stored_dices[ace] += exploding_dices
    ace[ace] &= (exploding_dices == dice_value)
    weapon = client.stored_values["players"][player]["weapon"]
    weapon_bonus = client.stored_values["players"][player]["weapon_bonus"]
    msg_bagarre = format_bagarre(player, jet, stored_dices, bonus_touch, bonus_dmg, weapon, weapon_bonus)
    await message.channel.send(msg_bagarre)
    for i in range(sum(ace)):
        with open('images/boum.jpg', 'rb') as fp:
            f = discord.File(fp)
            await message.channel.send(file=f)

async def cmd_test(message):
    """Une commande de test"""
    await message.channel.send(message.author)
    await message.channel.send(player_discord_names[str(message.author).split('#')[0]])

async def cmd_change_dices(message):
    """$value: Change le type des dés"""
    content = message.content
    try:
        dice_value = int(str(content).split(" ")[1])
        client.stored_values["dice_value"] = dice_value
        await message.channel.send("C'est toi le boss")
    except:
        await message.channel.send("Ya un truc qui va pas, format ';change_dice_value 8'")

async def draw_card(message, number, offset):
    boule = True
    player = get_player_name(message)

    while boule:
        new_card = random.randint(offset, offset + number)
        boule = new_card in all_cards(client.stored_values["cards"])
    await message.channel.send("Carte tirée : " + str(new_card))
    client.stored_values["cards"][player].append(new_card)
    store_cards(client)
    await send_card(message.channel,new_card)
    sort_cards(client)

async def cmd_exal(message):
    """$value: Tire $value cartes d'exhaltation"""
    await draw_card(message, 1, 53)

async def cmd_pers(message):
    """$value: Tire $value cartes de persécution"""
    await draw_card(message, 55, 18)

async def cmd_patr(message):
    """$value: Tire $value cartes de patrouille"""
    await draw_card(message, 73, 36)

async def cmd_drop_card(message):
    """$value: jette la carte $value"""
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

async def cmd_play(message):
    """$value: Joue la carte $value"""
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

async def cmd_cards(message):
    """Montre la liste des cartes des joueurs"""
    for key in client.stored_values["cards"].keys():
        await message.channel.send(key + " " + str(client.stored_values["cards"][key]))

async def cmd_get_card(message):
    """$value: Tire la carte $value"""
    try:
        card_number = int(str(content).split(" ")[1])
    except:
        await message.channel.send("Me faut un numéro de la carte mon goret")
        return
    await send_card(channel,card_number)

async def cmd_my_cards(message):
    """Affiche toutes les cartes du joueur (ça peut faire beaucoup)"""
    if " " in content:
        player = content.split(" ")[1]
    else:
        player = get_player_name(message)
    for card_number in client.stored_values["cards"][player]:
        await send_card(channel,card_number)

async def cmd_take(message):
    """$value $player: Prend $value"""
    content = message.content
    player = get_player_name(message)
    try:
        card_number = int(str(content).split(" ")[1])
    except:
        await message.channel.send("Me faut un numéro de la carte mon goret")
        return
    if card_number in all_cards(client.stored_values["cards"]):
        await message.channel.send("Quelqu'un a déjà la carte mon salaud")
        return
    client.stored_values["cards"][player].append(card_number)
    store_cards(client)
    await send_card(channel,card_number)

async def cmd_give(message):
    """$value $player: Donne $value à $player"""
    content = message.content
    player = get_player_name(message)

    try:
        card_number = int(str(content).split(" ")[1])
    except:
        await message.channel.send("Me faut un numéro de la carte mon goret")
        return
    try:
        receiver = str(content).split(" ")[2]
    except:
        await message.channel.send("Me faut le nom du joueur mon p'tit lou")
        return
    if receiver not in client.stored_values["cards"].keys():
        await message.channel.send("Jamais entendu parlé de ce gars là")
        return
    cards = client.stored_values["cards"][player]
    try:
        card_index = cards.index(card_number)
        cards.pop(card_index)
        await message.channel.send("Voilà voilà")
    except ValueError:
        await message.channel.send("T'as pas la carte mon chou")
        return
    client.stored_values["cards"][receiver].append(card_number)
    store_cards(client)

commands = {
    ';hello': cmd_hello,
    ';bagarre': cmd_bagarre,
    ';explode': cmd_explode,
    ';test': cmd_test,
    ';change_dices': cmd_change_dices,
    ';exal': cmd_exal,
    ';pers': cmd_pers,
    ';patr': cmd_patr,
    ';drop_card': cmd_drop_card,
    ';play': cmd_play,
    ';cards': cmd_cards,
    ';get_card': cmd_get_card,
    ';my_cards': cmd_my_cards,
    ';give': cmd_give,
    ';take': cmd_take,
    ';skills': cmd_skills
}

weapons_dict = {
        "1h_sword": "Epée",
        "2h_sword": "Epée à deux mains (+2 dégâts)",
        "1h_axe": "Hache (-1 CA contre combattants armés, +2 dégâts contre monstres",
        "2h_axe": "Hache à deux mains (-1 CA contre combattants armés, +4 dégâts contre monstres, +2 dégâts contre les autres)",
        "longbow": "Arc long",
        "shortbow": "Arc court",
        "spear": "Lance deux mains (+1 CA contre adversaires sans boucliers, +2 dégâts contre des grandes créatures ou cavaliers)",
        "dagger": "Dague (-2 CA contre adversaires avec arme plus longue, pas de malus en milieu confiné)",
        }

client = discord.Client()

classes =  ["soldat", "voyageur", "érudit", "archer", "assassin", "berzekr", "guerrier"]

client.stored_values = {
        "count" : 0,
        "dice_value" : 8,
        "ace":{},
        "dices":{},
        "jets":{},
        }

with open(file_name) as json_file:
    client.stored_values["cards"] = json.load(json_file)


with open(players_json) as json_file:
    client.stored_values["players"] = json.load(json_file)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    content = message.content
    command = content.split()[0]
    channel = message.channel
    player =get_player_name(message)

    print(get_player_name(message) + ' - ' + str(content))
    
    if command not in commands.keys() and command != ";help":
        await message.channel.send("Ca marcherait mieux si tu regardais ton clavier en tapant")
        return

    if command == ";help":
        help_msg = "\n".join([cmd + " " + func.__doc__ for cmd,func in commands.items()])
        await channel.send(help_msg)
    else:
        return await commands[command](message)


client.run(token)
