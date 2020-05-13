import numpy as np
import random
import json
import discord



file_name = "cards.json"
players_json = "players.json"
timeline_json = "timeline.json"
map_name = "map.npy"


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
    client.stored_values["jets"][player] = jet
    client.stored_values["dices"][player] = rolls
    ace = client.stored_values["ace"][player] = (rolls == dice_value)
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
        client.stored_values["players"] = json.load(json_file)

    with open("timeline.json") as json_file:
        client.stored_values["timeline"] = json.load(json_file)

def build_hexagon(origin,size):
    a,b  = origin
    c = size
    h = c*np.sqrt(3)/2
    g = c/2
    return ((a,b),(a+c,b),(a+c+g,b+h),(a+c,b+2*h),(a,b+2*h),(a-g,b+h))

def coordinate(x,y,size):
    c = size
    ga = c*2
    h = c*np.sqrt(3)/2
    alpha = (c+ga)/2
    beta = 110-3*(c+ga)/2
    alpha_y = 2*h
    beta_y = 100-6*h
    if not int(x/2)*2 == x:
        return alpha*x+beta,alpha_y*y+beta_y
    else:
        return alpha*x+beta,alpha_y*y+beta_y+h

def hex_coordinates(i,j,hex_size):
    x,y = coordinate(i,j,hex_size)
    poly = build_hexagon((x,y),hex_size)
    return poly
    
def draw_hex(draw,i,j,hex_size,color):
    poly = hex_coordinates(i,j,hex_size)
    draw.polygon(poly, color)

def draw_position(draw,x,y,hex_size):
    pos = hex_coordinates(x,y,hex_size)
    draw.line(pos, fill="red", width=7)

def load_map():
    return np.load(map_name)

def store_map(mapp):
    np.save(map_name,mapp)

