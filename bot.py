from config import token, players, MEUJEU, MEUJEU_ID,HEX_SIZE
from toolbox import *
from timeline import *
from player import *

import discord
import numpy as np
import random
import json
import pprint
from time import sleep
from PIL import Image, ImageDraw
import os


file_name = "cards.json"
players_json = "players.json"

async def cmd_hello(message):
    """Un p'tit coucou"""
    await message.channel.send("Fais pas le malin mon p'tit gars")

async def cmd_fight(message):
    """Commence un combat. L'initiative est lancée et quelques éléments d'information sur les combats sont affichés"""
    jet = "Initiative"
    msg_bagarre = "C'EST LA BAGARRE !\n1) Tirer les initiatives\n2) Se battre\n\t;bagarre soldat/guerrier/berzekr/archer\n\t;bagarre soldat $param - param peut être monster (applique les bonus de hache), armed (applique les malus de hache), meteo (applique les malus de meteo)\n3) Fin:\n\t1 point de ressource pour le groupe sinon affaiblis\n\t1 point de ressource par blessé sinon mort\n\tRécupérer points de ressources (si MJ dit OK)\n\n"

    for player_obj in client.stored_values["players_obj"].values():
        rolls,ace = roll(client,player_obj.name,jet, explode= not player_obj.skills["Affaibli"])
        _, init = player_obj.skill_check(jet, rolls, ace)
        msg_bagarre += _
        player_obj.init = init

    await message.channel.send(msg_bagarre)

async def cmd_bagarre(message):
    """$vocation/métier $param - Faire un jet de dé. Il est possible de préciser le type de jet ;bagarre type (soldat, voyageur, érudit, archer, assassin, berzekr, guerrier). On peut aussi passer certains paramètres (monster: attaque contre un monstre, armed: attaque contre des gens armés, meteo: prendre en compte la météo)"""

    player = get_player_name(message)
    jet, params = parse_bagarre(message) 
    player_obj = client.stored_values["players_obj"][player]

    rolls,ace = roll(client,player_obj.name,jet)
    player_obj.rolls, player_obj.ace = rolls, ace

    msg_bagarre, _ = player_obj.skill_check(jet, rolls, ace, params)
    await message.channel.send(msg_bagarre)
    for i in range(sum(ace)):
        with open('images/boum.jpg', 'rb') as fp:
            f = discord.File(fp)
            await message.channel.send(file=f)

def parse_bagarre(message):
    values = message.content.split()
    player = get_player_name(message)
    jet = None
    params = []
    if len(values) > 1:
        jet = values[1]
    if len(values) > 2:
        params = values[2:]
    if type(jet) == str:
        jet = jet.capitalize()
    return jet, params

async def cmd_skills(message,player=None):
    """Affiche les statistiques"""
    if player is None:
        if " " in message.content:
            player = message.content.split()[1]
            if player == "all":
                for p in client.stored_values["players_obj"].keys():
                    await cmd_skills(message,p)
        else:
            player = get_player_name(message)
        if player not in client.stored_values["players_obj"].keys():
            await message.channel.send("Jamais entendu de parler de ce gars là")
            return 
    
    player_obj = client.stored_values["players_obj"][player]
    msg = player_obj.format_skills()
    await message.channel.send(msg)

async def cmd_explode(message):
    """Relance les dés qui ont explosé au précédent jet du joueur"""
    player = get_player_name(message)
    player_obj = client.stored_values["players_obj"][player]
    dice_value = client.stored_values["dice_value"]
    jet = player_obj.jet
    ace = player_obj.ace
    stored_dices = player_obj.rolls
    params = player_obj.params
    if sum(ace) == 0:
        await message.channel.send("Fais pas le malin mon p'tit gars")
        return

    exploding_dices = roll_n_dices(sum(ace),dice_value,False)
    stored_dices[ace] += exploding_dices
    ace[ace] &= (exploding_dices == dice_value)

    msg_bagarre,_ = player_obj.skill_check(jet, stored_dices, ace, params)

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
    try:
        card_number = int(str(message.content).split(" ")[1])
    except:
        card_number = 1
    if card_number > 6:
        await message.channel.send("Ca fait beaucoup de cartes non?")
        return
    
    for i in range(card_number):
        draw = list(range(number, offset + number + 1))
        for card in all_cards(client.stored_values["cards"]):
            if card in draw:
                draw.remove(card)
        if len(draw) < 5:
            draw.append(client.stored_values["cards"]["discard"])
            client.stored_values["cards"]["discard"] = []
        new_card = random.choice(draw)
        await message.channel.send("Carte tirée : " + str(new_card))
        await send_card(message.channel,new_card)
        sort_cards(client)
        return new_card

async def cmd_exal(message):
    """$value: Tire $value cartes d'exhaltation"""
    player = get_player_name(message)
    if len(message.content.split()) > 1:
        nb_cards = int(message.content.split()[1])
    else:
        nb_cards = 1
    for i in range(nb_cards):
        new_card = await draw_card(message, 1, 53)
        client.stored_values["cards"][player].append(new_card)
    sort_cards(client)
    store_cards(client)

async def cmd_pers(message):
    """$value: Tire $value cartes de persécution"""
    player = get_player_name(message)
    if len(message.content.split()) > 1:
        nb_cards = int(message.content.split()[1])
    else:
        nb_cards = 1
    for i in range(nb_cards):
        new_card = await draw_card(message, 55, 18)
        client.stored_values["cards"][player].append(new_card)
    sort_cards(client)
    store_cards(client)

async def cmd_patr(message):
    """$value: Tire $value cartes de patrouille"""
    player = get_player_name(message)
    if len(message.content.split()) > 1:
        nb_cards = int(message.content.split()[1])
    else:
        nb_cards = 1
    for i in range(nb_cards):
        new_card = await draw_card(message, 73, 36)
        weather_tuple = weather[client.stored_values["timeline"]["weather"]]
        special = client.stored_values["timeline"]["special"]
        msg = "Rappel météo: %s" % weather_tuple[1]
        if special != None:
            msg +=" - %s" % special_weather[special][1]
        await message.channel.send(msg)

        if new_card >= 97:
            client.stored_values["cards"][player].append(new_card)
            sort_cards(client)
            store_cards(client)
        else:
            weather_modif = client.stored_values["timeline"]["weather_modif"]
            rolls,ace = roll(client,MEUJEU,"patrouille",8,2,True)
            msg = """Jet de patrouille de %s : %d (Dés: %d,%d Temps: %d)""" % (player,int(np.sum(rolls))+client.stored_values["timeline"]["weather_modif"] + weather_modif, rolls[0], rolls[1], weather_modif)
            meujeu = await client.fetch_user(MEUJEU_ID)
            await meujeu.send(msg)

async def cmd_drop_card(message):
    """$value: jette la carte $value"""
    player = get_player_name(message)
    try:
        card_number = int(str(message.content).split(" ")[1])
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
        card_number = int(str(message.content).split(" ")[1])
    except:
        await message.channel.send("Me faut un numéro de la carte mon goret")
        return
    cards = client.stored_values["cards"][player]
    discard = client.stored_values["cards"]["discard"]
    try:
        card_index = cards.index(card_number)
        cards.pop(card_index)
        discard.append(card_number)
        print(discard)
    except ValueError:
        await message.channel.send("T'as pas la carte mon chou")
        return
    await send_card(message.channel,card_number)
    store_cards(client)

async def cmd_cards(message):
    """Montre la liste des cartes des joueurs"""
    msg = ""
    for key in client.stored_values["cards"].keys():
        msg += key + " " + str(client.stored_values["cards"][key])+"\n"

    await message.channel.send(msg)

async def cmd_get_card(message):
    """$value: Tire la carte $value"""
    try:
        card_number = int(str(message.content).split(" ")[1])
    except:
        await message.channel.send("Me faut un numéro de la carte mon goret")
        return
    await send_card(message.channel,card_number)

async def cmd_my_cards(message):
    """Affiche toutes les cartes du joueur (ça peut faire beaucoup)"""
    if " " in message.content:
        player = message.content.split(" ")[1]
    else:
        player = get_player_name(message)
    for card_number in client.stored_values["cards"][player]:
        await send_card(message.channel,card_number)

async def cmd_take(message):
    """$value : Prend $value"""
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
    await send_card(message.channel,card_number)

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

async def cmd_drop_hand(message):
    """Drop la main du joueur"""
    player = get_player_name(message)

    client.stored_values["cards"]["discard"] += client.stored_values["cards"][player]
    client.stored_values["cards"][player] = []
    store_cards(client)

    await message.channel.send("Voilà Voilà")

async def cmd_day(message):
    """Affiche les informations de la journée"""
    await message.channel.send(get_date(client.stored_values["timeline"]))

async def cmd_next_day(message):
    """Passe au jour suivant"""
    client.stored_values["timeline"]["weather"], client.stored_values["timeline"]["weather_modif"], client.stored_values["special"], client.stored_values["timeline"]["observation"] = roll_meteo(client.stored_values["timeline"]["weather"])
    client.stored_values["timeline"]["day"] += 1
    client.stored_values["timeline"]["hunger"] += 1
    await message.channel.send(get_date(client.stored_values["timeline"]))
    store_timeline(client)

async def cmd_ellipse(message):
    """$value - Effectue une ellipse de $value jours."""
    params = message.content.split()
    if len(params) > 1:
        ellipse_days = int(params[1])
        client.stored_values["timeline"]["weather"], client.stored_values["timeline"]["weather_modif"], client.stored_values["special"], client.stored_values["timeline"]["observation"] = roll_meteo(client.stored_values["timeline"]["weather"])
        client.stored_values["timeline"]["day"] += ellipse_days
        store_timeline(client)
        await message.channel.send(get_date(client.stored_values["timeline"]))
    else:
        await message.channel.send("Il manque un argument mon chou")


async def cmd_record_event(message):
    """$duration $event - Enregistre un événement $event qui sera réaffiché pendant $duration jours."""
    duration = int(message.content.split()[1])
    event = " ".join(message.content.split()[2:])
    day = client.stored_values["timeline"]["day"]
    client.stored_values["timeline"]["events"].append({'duration': duration, 'date_record':day, 'event': event})
    store_timeline(client)
    await message.channel.send("Evénement enregistré !")

async def cmd_eat(message):
    """Indique que le groupe a mangé (ne gère pas les cas où juste une partie du groupe mange"""
    client.stored_values["timeline"]["hunger"] = 0
    store_timeline(client)
    await message.channel.send("Le groupe a mangé.\n\n\"*Il est nécessaire de s'alimenter régulièrement sinon c'est la mort assurée !*\"\n\t- *Manuel du patrouilleur, Chapitre IX: Comment ne pas mourir lors de sa première patrouille*\n")

async def cmd_load(message):
    """Reload tous les fichiers (cartes, joueurs, skills,...) - Commande réservée au MJ"""
    player = get_player_name(message)
    if player != MEUJEU:
        await message.channel.send("Ha bah non en fait")
        return
    load(client)
    await message.channel.send("Voilà Voilà")

async def cmd_pv(message):
    """$value - Modifie les PV de $value. Affiche les PV si pas de $value"""
    params = message.content.split()
    player = get_player_name(message)
    if len(params) > 1:
        client.stored_values["players_obj"][player].change_pv(int(params[1]))
        store_players(client)
    await message.channel.send(client.stored_values["players_obj"][player].format_pv())

async def cmd_status(message):
    """$value - Modifie le status $value (affaibli, en danger ou contraint)"""
    params = message.content.split()
    player = get_player_name(message)
    if len(params) == 0:
        await message.channel.send(";status [%s]" % ", ".join(status))
    elif len(params) > 1:
        new_status = " ".join(params[1:]).capitalize()
        if new_status not in status:
            await message.channel.send("Il faut mettre %s" % ", ".join(status))
            return
        client.stored_values["players_obj"][player].change_status(new_status)
        store_players(client)
    await message.channel.send("Voilà voilà")

async def cmd_reset_meteo(message):
    """Reset la météo pour qu'elle corresponde à la saison (à utiliser en cas de déviation trop importante)"""
    client.stored_values["timeline"]["weather"], client.stored_values["timeline"]["weather_modif"], client.stored_values["special"], client.stored_values["timeline"]["observation"] = reset_meteo(client)
    store_timeline(client)
    await message.channel.send(get_date(client.stored_values["timeline"]))

async def cmd_map(message):
    """Affiche la carte du monde""" 

    colors = [
        (255, 0, 0, 75),
        (255, 255, 0, 75),
        (255, 0, 255, 75),
        (0, 0, 255, 75),
        (0, 225, 255, 75),
        (0, 255, 0, 75),
    ]

    mapp = load_map()

    #im = Image.open("carte_hexagon.png")
    im = Image.open("images/world_map.png")
    im = im.convert('RGB')

    draw = ImageDraw.Draw(im,"RGBA")

    for i, j in np.ndindex(mapp.shape):
        if mapp[i,j]:
            draw_hex(draw,i,j,HEX_SIZE,colors[int(mapp[i,j])-1])


    position_str = client.stored_values["timeline"]["position"]
    position = tuple(map(int,position_str.split(",")))

    draw_position(draw,*position,HEX_SIZE)
    im.save("temp_map.png")
    with open("temp_map.png","rb") as fp:
        f = discord.File(fp)
        await message.channel.send(file=f)
    os.remove("temp_map.png")


async def cmd_move(message):
    """$x,$y : Déplace le groupe sur la case indiquée"""
    content = message.content
    if len(content.split(" ")) == 1:
        await message.channel.send("Mon loulou, si tu me dis pas où tu veux aller, je vais pas pouvoir t'y emmener")
        return
    try:
        position_str = content.split(" ")[1]
        x,y = tuple(map(int,position_str.split(",")))
    except:
        await message.channel.send("J'ai rien compris...")
        return
    client.stored_values["timeline"]["position"]  = position_str
    await message.channel.send("Voilà Voilà")


async def cmd_en_avant(message):
    """Tu vois ce que je veux dire"""
    content = message.content
    if len(content.split(" ")) == 1:
        await message.channel.send("Mon loulou, si tu me dis pas où tu veux aller, je vais pas pouvoir t'y emmener")
        return
    try:
        position_str = content.split(" ")[1]
        x,y = tuple(map(int,position_str.split(",")))
    except:
        await message.channel.send("J'ai rien compris...")
        return

    position_str = client.stored_values["timeline"]["position"]
    cx,cy = tuple(map(int,position_str.split(",")))

    boule = False
    #Test if motion is an hexagon wide
    boule = boule or (abs(cx-x) > 1 or abs(cy-y) > 1)
    #Test if x is odd
    boule = boule or (cx != x and cx & 1 and y == cy+1)
    #Test if x is even
    boule = boule or (cx != x and not(cx & 1) and y == cy-1)
    #Boule is True if the move is invalid
    if boule:
        await message.channel.send("Dans la vie jeune patrouilleur, on avance un pas après l'autre") 
        return

    client.stored_values["timeline"]["position"] = str(x)+","+str(y)
    mapp = load_map()
    mapp[x,y] += 1
    mapp = np.clip(mapp,0,6)
    store_map(mapp)
    await cmd_map(message)
    message.content = ""
    await cmd_patr(message)

def cmd_rules(message):
    """$value - Affiche des informations sur les règles."""
    rules = ["prouesse"]
    params = message.content.split()
    msg = ""
    if len(params) > 1 and params[1] in rules:
        if params[1] == "prouesse":
            msg = "Règles de prouesse\n"
            msg +="\n".join(["%d - %s" % (i, prouesse[i][0]) for i in range(4)])

async def cmd_legend(message):
    """Légende de la carte"""

    with open("images/legend.png","rb") as fp:
        f = discord.File(fp)
        await message.channel.send(file=f)

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
    ';skills': cmd_skills,
    ';drop_hand' : cmd_drop_hand,
    ';day' : cmd_day,
    ';next_day' : cmd_next_day,
    ';record_event': cmd_record_event,
    ';eat': cmd_eat,
    ';load': cmd_load,
    ';map' : cmd_map,
    ';move' : cmd_move,
    ';en_avant' : cmd_en_avant,
    ';fight': cmd_fight,
    ';pv': cmd_pv,
    ';status': cmd_status,
    ';ellipse' : cmd_ellipse,
    ';reset_meteo' : cmd_reset_meteo,
    ';legend' : cmd_legend,
    ';rules' : cmd_rules,
}


client = discord.Client()
client.stored_values = {
        "dice_value" : 8,
        "ace":{},
        "dices":{},
        "jets":{},
        "players": {},
        }
load(client)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user or message.content[0] != ';':
        return
    try:
        command = message.content.split()[0]
        channel = message.channel
        player =get_player_name(message)

        print(get_player_name(message) + ' - ' + str(message.content))
        
        if command not in commands.keys() and command != ";help":
            await message.channel.send("Ca marcherait mieux si tu regardais ton clavier en tapant")
            return

        if command == ";help":
            help_msg = "\n".join([cmd + " " + func.__doc__ for cmd,func in commands.items()])
            await channel.send(help_msg)
        else:
            return await commands[command](message)
    except Exception as e:
        await message.channel.send("Il s'est passé un truc qui devait pas se passer comme on avait dit que ça devait se passer")
        sleep(1.5)
        await message.channel.send("Enfin je crois")
        raise Exception(e)


client.run(token)
