import numpy as np
import random
import json
import discord



file_name = "cards.json"
players_json = "players.json"


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


