from config import token, players, MEUJEU, MEUJEU_ID
from toolbox import *
from timeline import *

import discord
import numpy as np
import random
import json
import pprint
from time import sleep

file_name = "cards.json"
players_json = "players.json"

async def cmd_hello(message):
    """Un p'tit coucou"""
    await message.channel.send("Fais pas le malin mon p'tit gars")


async def cmd_bagaarre(message):
    """Lance l'initiative pour tous les joueurs"""
    jet = "Initiative"
    client.stored_values["init"] = {}
    for player in client.stored_values["players"].keys():
            bonus_touch, bonus_dmg, jet = get_bonus(jet,player)+(jet,)
            rolls,ace = roll(client,player,jet,explode=True)
            msg_bagarre,init = format_bagarre(player,jet,rolls,bonus_touch,bonus_dmg)
            client.stored_values["init"][player] = init
            await message.channel.send(msg_bagarre)

async def cmd_bagarre(message):
    """Faire un jet de dé. Il est possible de préciser le type de jet ;bagarre type (soldat, voyageur, érudit, archer, assassin, berzekr, guerrier)"""

    bonus_touch, bonus_dmg, jet = parse_bagarre(message) 
    player = get_player_name(message)

    rolls,ace = roll(client,player,jet)

    weapon = client.stored_values["players"][player]["Arme"]
    weapon_bonus = client.stored_values["players"][player]["Arme bonus"]
    msg_bagarre,_ = format_bagarre(player, jet, rolls, bonus_touch, bonus_dmg, weapon, weapon_bonus)
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
    if type(jet) == str:
        jet = jet.capitalize()
    return get_bonus(jet, player) + (jet,)

def get_bonus(jet, player):
    bonus_touch = 0
    bonus_dmg = 0
    if jet in classes:
        if jet in vocations:
            bonus_touch = client.stored_values["players"][player][jet]
        else:
            bonus_touch = client.stored_values["players"][player]["Soldat"]
            if jet == "Berzekr": # Bonus de berzekr + bonus de guerrier
                bonus_touch += client.stored_values["players"][player]["Berzekr"]
                bonus_dmg = client.stored_values["players"][player]["Berzekr"]
                bonus_dmg += client.stored_values["players"][player]["Guerrier"]
            elif jet in ["Guerrier", "Archer"]:
                bonus_dmg = client.stored_values["players"][player][jet]
    elif jet == "Initiative":
        bonus_touch = client.stored_values["players"][player]["Soldat"]
    return bonus_touch, bonus_dmg

def format_bagarre(player, jet, rolls, bonus_touch, bonus_dmg, weapon=None, weapon_bonus = 0):
    rolls_txt = " ".join(map(lambda x : str(int(x)),rolls))
    mait, prou, exalt = map(lambda x: int(x), rolls)
    best_score = np.sum(np.sort(np.array((mait,prou,exalt)))[1:3])
    #Préciser la nature du jet
    if jet:
        if jet in vocations:
            msg = "**Jet de vocation (%s) de %s**\n" % (jet, player)
        elif jet == "Guerrier":
            msg = "**Jet de combat (%s) de %s**\n" % (jet, player)
        elif jet == "Berzekr":
            msg = "**Jet de combat (%s) de %s**. (Le bonus de guerrier est pris en compte).\n" % (jet, player)
        elif jet == "Archer":
            msg = "**Jet de combat (%s) de %s**. Malus pour les tirs à grande distance.\n" %(jet, player) 
        elif jet == "Initiative":
            msg = "**Jet d'initiative de %s**\n" % (player)
        else:
            msg = "**Jet de machin de %s**. En vrai %s c'est pas parmi les trucs supportés donc va falloir appliquer les bonus à la main ou vérifier que tu aies pas écrit n'importe quoi. Bisous.\n" % (player, jet)
    else:
        msg = "Jet standard de %s\n" % player
    #Préciser l'arme utilisé
    if weapon:
        msg += "Arme (les dégâts à appliquer manuellement): %s\n" % weapons_dict[weapon]
    #Préciser les bonus de l'arme
    if weapon_bonus:
        msg += "Bonus arme (à appliquer): + %d dégâts\n" % int(weapon_bonus)
    msg += "Jet: %s (Bonus touche: %d, Bonus dégâts: %d)\n" % (rolls_txt, bonus_touch, bonus_dmg)
    #Préciser le résultat du jet (le meilleur est donné dans le cas d'un jet d'initiative
    if jet == "Initiative":
        msg += "Inititative de %s : %d\n\n\n" %(player,best_score+bonus_touch)
    else:
        msg += "%d (%d dégâts%s) ou %d (%d dégâts%s) ou %d (%d dégâts%s)" % (
                mait + prou + bonus_touch,
                mait + bonus_dmg,
                ", prouesse " + str(prou) if prou < 5 else "",
                mait + exalt + bonus_touch,
                mait + bonus_dmg,
                ", prouesse " + str(exalt) if exalt < 5 else "",
                exalt + prou + bonus_touch,
                exalt + bonus_dmg,
                ", prouesse " + str(prou) if prou < 5 else "")
    return msg,best_score

async def cmd_skills(message,player=None):
    """Affiche les statistiques"""
    if player is None:
        if " " in message.content:
            player = message.content.split()[1]
            if player == "all":
                for p in client.stored_values["players"].keys():
                    await cmd_skills(message,p)
        else:
            player = get_player_name(message)
        if player not in client.stored_values["players"].keys():
            await message.channel.send("Jamais entendu de parler de ce gars là")
            return 
    player_skills = client.stored_values["players"][player]
    msg = "**Compétences de %s" % player + "**"
    msg += "\n*CA*: %s *Mana*: %s *PV Max*: %s *Vigilance:* %s" % (10+sum(list(map(lambda x : player_skills[x],armor)))+int(player_skills["Guerrier"]/2),player_skills["DV"]*2+player_skills["Érudit"],player_skills["PV Max"],10+player_skills["Voyageur"]+int(player_skills["Assassin"]/2))
    msg += "\n**Vocations**\n"
    msg += " ".join(["%s : %s" % ("*"+vocation+"*",player_skills[vocation]) for vocation in vocations])
    msg += "\n**Métiers**\n"
    msg += " ".join(["%s : %s" % ("*"+job+"*",player_skills[job]) for job in jobs if str(player_skills[job])!='0'])
    msg += "\n**Armes**\n"
    temp = ["%s : %s" % ("*"+weapon+"*",player_skills[weapon]) for weapon in weapons if str(player_skills[weapon])!='0']
    if temp == []:
        msg += "Nada"
    else:
        msg += " ".join(temp)
    msg += "\n**Armures**\n"
    temp = ["%s : %s" % ("*"+armor+"*",player_skills[armor]) for armor in armor if str(player_skills[armor])!='0']
    if temp == []:
        msg += "Nada"
    else:
        msg += " ".join(temp)
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
    weapon = client.stored_values["players"][player]["Arme"]
    weapon_bonus = client.stored_values["players"][player]["Arme bonus"]
    msg_bagarre,_ = format_bagarre(player, jet, stored_dices, bonus_touch, bonus_dmg, weapon, weapon_bonus)
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
        boule = True
        while boule:
            new_card = random.randint(number, offset + number)
            boule = new_card in all_cards(client.stored_values["cards"])
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
        if new_card >= 97:
            client.stored_values["cards"][player].append(new_card)
            sort_cards(client)
            store_cards(client)
        else:
            rolls,ace = roll(client,MEUJEU,"patrouille",8,2,True)
            msg = """Jet de patrouille de %s : %s""" % (player,int(np.sum(rolls)))
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
    try:
        card_index = cards.index(card_number)
        cards.pop(card_index)
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

    client.stored_values["cards"][player] = []

    await message.channel.send("Voilà Voilà")

async def cmd_day(message):
    """Affiche les informations de la journée"""
    await message.channel.send(get_date(client.stored_values["timeline"]))

async def cmd_next_day(message):
    """Passe au jour suivant"""
    client.stored_values["timeline"]["weather"], client.stored_values["timeline"]["weather_modif"] = roll_meteo(client.stored_values["timeline"]["weather"])
    client.stored_values["timeline"]["day"] += 1
    client.stored_values["timeline"]["hunger"] += 1
    await message.channel.send(get_date(client.stored_values["timeline"]))
    store_timeline(client)

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
        await message.channel.send("Fais pas le malin mon p'tit gars")
        return
    load(client)
    await message.channel.send("Voilà Voilà")


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
    ';bagaarre': cmd_bagaarre,
}

weapons_dict = {
        "1h_sword": "Epée",
        "2h_sword": "Epée à deux mains (+2 dégâts)",
        "1h_axe": "Hache (-1 à l'attaque contre combattants armés, +2 dégâts contre monstres",
        "2h_axe": "Hache à deux mains (-1 à l'attaque contre combattants armés, +4 dégâts contre monstres, +2 dégâts contre les autres)",
        "longbow": "Arc long",
        "shortbow": "Arc court",
        "spear": "Lance deux mains (+1 CA contre adversaires sans boucliers, +2 dégâts contre des grandes créatures ou cavaliers)",
        "dagger": "Dague (-2 CA contre adversaires avec arme plus longue, pas de malus en milieu confiné)",
        }

client = discord.Client()

classes =  ["Soldat", "Voyageur", "Érudit", "Archer", "Assassin", "Berzekr", "Guerrier"]

client.stored_values = {
        "dice_value" : 8,
        "ace":{},
        "dices":{},
        "jets":{},
        }

vocations = ["Soldat","Voyageur","Érudit"]
jobs = ["Archer","Assassin","Berzekr","Guerrier","Druide","Maître des bêtes"]
weapons = ["Arme","Arme bonus"]
armor = ["Armure","Bouclier"]


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
