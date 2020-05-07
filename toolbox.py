import numpy as np
import random
import json
import discord
from player import Player



file_name = "cards.json"
players_json = "players.json"
timeline_json = "timeline.json"


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

def roll(client,player,jet,dice_value=None,dice_number=3,explode=False):
    if dice_value is None:
        dice_value = client.stored_values["dice_value"]
    rolls = roll_n_dices(dice_number,dice_value,explode)

    ace = (rolls == dice_value)
    return rolls,ace

def get_sum(rolls):
    sorted_rolls = np.sort(rolls)
    return int(sum(sorted_rolls[-2:]))

def all_cards(cards):
    all_cards = []
    for key in cards.keys():
        all_cards.extend(cards[key])
    return all_cards

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

def store_timeline(client):
    cards = client.stored_values["timeline"]
    with open(timeline_json, 'w') as fp:
        json.dump(cards, fp)

def load(client):
    with open(file_name) as json_file:
        client.stored_values["cards"] = json.load(json_file)

    with open(players_json) as json_file:
        #client.stored_values["players"] = json.load(json_file)
        client.stored_values["players_obj"] = {}
        for name, skills in json.load(json_file).items():
            client.stored_values["players_obj"][name] = Player(name, skills)

    with open("timeline.json") as json_file:
        client.stored_values["timeline"] = json.load(json_file)

