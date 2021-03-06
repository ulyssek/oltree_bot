import random

seasons = ["Printemps", "Eté", "Automne", "Hiver"]
weeks = ["Basse", "Haute", "Fuyante"]
months = ["placeholder"] * 3 + ["Molosse ailé", "Numismate","Frondeur", "Chat noir", "Faucheur", "Reine barbare", "Guide"] + ["placeholder"] * 5 * 2

weather=[
            ("Pluies fines", "Une légère pluie tombe sur la région", False, range(1,4),"https://gph.is/2gYLREp"),
        ("Giboulées", "Le temps est relativement calme mais quelques giboulées tombent de temps en temps", True, range(0),"https://gph.is/2gYLREp"),
        ("Averses locales", "Des averses tombent sur la région.", True, range(2),"https://gph.is/2gYLREp"),
        ("Nuages et vent", "Quelques nuages et du vent.", True, range(1,4),"https://gph.is/2CHmA9j"),
        ("Eclaircies et vent", "Quelques nuages et un vent qui souffle du nord", True, range(1,4),"https://gph.is/2CHmA9j"),
        ("Beau temps nuageux", "Une belle journée malgré quelques nuages", True, [],"https://gph.is/2CHmA9j"),
        ("Beau temps", "Une belle journée !", True, [],"https://gph.is/1prsxYn"),
        ("Grand beau temps", "Une journée magnifique !", True, [],"https://gph.is/1prsxYn"),
        ("Lourd et orageux", "Un temps de chien. Des torrents de pluie s'abattent sur la patrouille et le tonnerre gronde.", False, range(1,3),"https://gph.is/2gtl6WV"),
        ("Caniculaire", "Une température caniculaire qui donne envie de rester à l'ombre", True, [],"https://gph.is/1prsxYn"),
        ("Grand beau temps", "Une journée magnifique !", True, [],"https://gph.is/1prsxYn"),
        ("Beau temps", "Une belle journée !", True, [],"https://gph.is/1prsxYn"),
        ("Beau temps", "Une belle journée !", True, [],"https://gph.is/1prsxYn"),
        ("Beau temps nuageux", "Une belle journée malgré quelques nuages", True, [],"https://gph.is/2CHmA9j"),
        ("Eclaircies", "Quelques nuages mais rien de grave", True, [],"https://gph.is/2CHmA9j"),
        ("Eclaircies et vent", "Un temps nuageux et un vent qui souffle du nord", True, range(1,4),"https://gph.is/2CHmA9j"),
        ("Pluies et vent", "Une journée pleine de pluie et de vent...", False, [i + j for i in range(1,4) for j in range(1,4)],"https://gph.is/2gYLREp"),
        ("Vents violents", "Un vent très fort souffle sur la région", True, range(2,4)),
        ("Pluies froides", "Il ne cesse de pleuvoir, attention à ne pas attraper la crève", False, range(1,4),"https://gph.is/2gYLREp"),
        ("Gelées", "Un froid glacial s'est abattu sur la région", True, [],"https://gph.is/2CJ9E3A"),
        ("Froid intense, ciel dégagé", "Un froid intense s'est abattu sur la région. Heureusement le soleil pointe le bout de son nez", True, [],"https://gph.is/2CJ9E3A"),
        ("Neige", "La neige tombe sur la région", False, range(2,6),"https://gph.is/Vx9tNX"),
        ("Gelées verglaçantes", "Un froid terrible s'est abattu sur la région. Les lacs et rivières sont gelés.", True, [],"https://gph.is/2CJ9E3A"),
        ("Pluies froides", "Un torrent de pluie glacé nous tombe dessus", True, range(1,4),"https://gph.is/2gYLREp")
        ]

special_weather = [
        ("Pied-de-vent", "Le temps est nuageux mais des rayons de lumière traversent le ciel", True, 0),
        ("Bourrasques (vent)", "Le temps est venteux et de violentes bourrasques soufflent parfois sur la région.", True, 1),
        ("Brumes (Mod +1)", "Le temps est brumeux mais il reste possible de s'orienter. (Malus sur le déplacement)", False, 1),
        (u"Grèle (Mod +1)", "Une journée où la grèle tombe.", True, 1),
        ("Orage (Mod +2)", "Orage et pluie ! Que du bonheur.", False, 2,"https://gph.is/1PBO1yL"),
        ("Brouillards épais (Mod +2)", "Un brouillard très épais est tombé sur la région. Attention à ne pas vous perdre (Malus sur le déplacement, risque de se retrouver sur le mauvais hexagone)", False, 2),
        (u"Rafales très violentes (Mod +3)", "Des rafales de vent violentes soufflent sur la région", True, 3), 
        (u"Poussières corrompues (vigueur contre poison) (Mod +4)", "Depuis la grande guerre contre le roi sorcier des vents empoisonnés soufflent de temps en temps sur l'empire. Les gens s'enferment chez eux dans ces cas et prient pour que le bétail et les récoltes ne succombent pas tous. (Jet de vigueur contre poison si vous sortez).", True, 4)
        ]

hours = [
        ("Nuit (1/2)", "\"Il est recommandé de dormir la nuit car la fatigue est un des pires ennemis du patrouilleur. Seules les liches, géants de feu, brigands, gobelins, gnolls, orcs des prairies de sable, agents du roi sorcier sont pires que la fatigue.\"\n\t- *Manuel du patrouilleur, Chapitre VI: Les menaces qui rodent dans l'Empire*\n"),
        ("Nuit (2/2)", "\"Il est recommandé de dormir la nuit car la fatigue est un des pires ennemis du patrouilleur. Seules les liches, géants de feu, brigands, gobelins, gnolls, orcs des prairies de sable, agents du roi sorcier sont pires que la fatigue.\"\n\t- *Manuel du patrouilleur, Chapitre VI: Les menaces qui rodent dans l'Empire*\n"),
        ("Aube", "\"Le lever du soleil est le meilleur moment pour effectuer sa prière quotidienne.\"\n\t- *Manuel du patrouilleur, Chapitre II: Comment les dieux peuvent vous sauver*\n"),
        ("Matinée", "\"Traditionnellement la matinée est consacrée à l'entrainement physique et intellectuel.\"\n\t- *Manuel du patrouilleur, Chapitre IV: Que faire quand on est un patrouilleur*\n"),
        ("Midi", "\"Le milieu de la journée est appelé midi.\"\n\t- *Manuel du patrouilleur, Chapitre XIX: Midi*\n"),
        ("Après-midi", "\"L'après-midi constitue le moment idéal pour faire sa patrouille pour de nombreuses raisons. Ces raisons sont cependant trop nombreuses pour être explicitées ici et vous devrez donc faire confiance à ce que je dis.\"\n\t- *Manuel du patrouilleur, Chapitre XIII: De l'importance de l'après-midi*\n"),
        ("Soirée", "\"Il n'y a rien de plus magnique que le soleil couchant sur les plaines vertes d'Ambrasie.\"\n\t- *Manuel du patrouilleur, Chapitre V: Aparté sur les magnifiques terres d'Ambrasie*\n"),
        ("Soir", "\"Le soir de nombreux dangers peuvent guetter le patrouilleur. Donc faites gaffe!\"\n\t- *Manuel du patrouilleur, Chapitre VI: Les menaces qui rodent sur l'Empire\n"),
        ]

def next_day(client):
    client.stored_values["timeline"]["day"] += 1
    client.stored_values["timeline"]["weather"], client.stored_values["timeline"]["weather_modif"], client.stored_values["timeline"]["special"], client.stored_values["timeline"]["observation"] = roll_meteo(client.stored_values["timeline"]["weather"])
    client.stored_values["timeline"]["hunger"] += 1

def get_date(date):
    season = int(date["day"] / (6 * 3 * 5))
    month = int(date["day"] / (6 * 3))
    week = int(date["day"] / 6) % 3
    weekday = date["day"] % 6 

    msg = "*Jour %d, %s de %s (%s), %s %d*\n\n" % (
            weekday+1,
            weeks[week],
            months[month],
            seasons[season],
            date["ext"],
            date["year"],
            )
    current_weather = weather[date["weather"]][1]
    msg += "**Météo**\nTemps: %s\n" % weather[date["weather"]][1]
    if date["special"]:
        msg += "Special: %s\n" % special_weather[date["special"]][1]
    observation = "Observation possible"
    modif = 0
    if "pluie" in current_weather.lower():
        observation = "Observation impossible"
    if "neige" in current_weather.lower():
        observation = "Observation impossible"
    msg += "%s - Modif. péripétie et attaque à distance: %d\n" % (observation, date["weather_modif"])
    msg += "\n**Statut du groupe**\n"
    for event in date["events"]:
        ecart = event["date_record"] + event["duration"] - date["day"]
        if ecart > 0:
            msg += "%s (%d jours restants)\n" % (event["event"], ecart+1)
        elif ecart == 0:
            msg += "%s (Dernier jour)\n" % event["event"]
        else:
            # Supprimer l'event
            pass 
    msg += get_hunger(date)
    msg += '\n'
    msg += weather[date["weather"]][-1]
    return msg

def get_hunger(date):
    hunger = date["hunger"]
    faim = [
        "Faim: tout va bien - Nécessaire: rien\n",
        "Faim: tout va bien - Nécessaire: 1 RU/pers sinon affaibli, pas de récupération de PV/mana, mort des blessés.\n",
        "Faim: Affaibli, pas de récupération de PV, mort des blessés - Nécessaire: 1 RU/pers sinon affaibli & en danger, pas de récup de PV/mana, PV max divisé par 2, mort des blessés.\n",
        "Faim: Affaibli & en danger, pas de récupération de PV, PV max divisé par 2, mort des blessés - Nécessaire: 1 RU/pers sinon affaibli & en danger, pas de récup de PV/mana, PV max divisé par 2, mort des blessés.\n",
        "Faim: Affaibli & en danger, pas de récupération de PV, PV max divisé par 2, mort des blessés - Nécessaire: 1 RU/pers sinon mort.\n",
        "Faim: Mort (sauf cas exceptionnel) - Nécessaire: 1 RU/pers\n",
        ]
    return faim[hunger]

def reset_meteo(client):
    season = int(client.stored_values["timeline"]["day"] / (6 * 3 * 5))
    return roll_meteo(season * 6 + 3)

def roll_meteo(starter):
    if not starter and starter != 0:
        starter = random.randint(0,len(weather))
    new_weather = starter
    special = None
    modif = 0
    res = random.randint(1,8)
    if res < 3:
        new_weather = starter + random.randint(-4,-1)
    elif res > 5 and res < 8:
        new_weather = starter + random.randint(-4,-1)
    elif res == 8:
        special = random.choice(range(0, len(special_weather)))

    observation = weather[new_weather][2] and (not special or special_weather[special][2])

    if len(weather[new_weather][3]) > 0:
        modif = random.choice(weather[new_weather][3])
    if special:
        modif += special_weather[special][3]
    return new_weather, modif, special, observation
