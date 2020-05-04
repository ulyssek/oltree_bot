import random

seasons = ["Printemps", "Eté", "Automne", "Hiver"]
weeks = ["Basse", "Haute", "Fuyante"]
months = ["placeholder"] * 3 + ["Molosse ailé", "Numismate","Frondeur", "Chat noir", "Faucheur", "Reine barbare", "Guide"] + ["placeholder"] * 5 * 2

weather=[
        ("Pluies fines", "Une légère pluie tombe sur la région"),
        ("Giboulées", "Le temps est relativement calme mais quelques giboulées tombent de temps en temps"),
        ("Averses locales", "Des averses tombent sur la région."),
        ("Nuages et vent", "Quelques nuages et du vent."),
        ("Eclaircies et vent", "Quelques nuages et un vent qui souffle du nord"),
        ("Beau temps nuageux", "Une belle journée malgré quelques nuages"),
        ("Beau temps", "Une belle journée !"),
        ("Grand beau temps", "Une journée magnifique !"),
        ("Lourd et orageux", "Un temps de chien. Des torrents de pluie s'abattent sur la patrouille et le tonnerre gronde."),
        ("Caniculaire", "Une température caniculaire qui donne envie de rester à l'ombre"),
        ("Grand beau temps", "Une journée magnifique !"),
        ("Beau temps", "Une belle journée !"),
        ("Beau temps", "Une belle journée !"),
        ("Beau temps nuageux", "Une belle journée malgré quelques nuages"),
        ("Eclaircies", "Quelques nuages mais rien de grave"),
        ("Eclaircies et vent", "Un temps nuageux et un vent qui souffle du nord"),
        ("Pluies et vent", "Une journée pleine de pluie et de vent..."),
        ("Vents violents", "Un vent très fort souffle sur la région"),
        ("Pluies froides", "Il ne cesse de pleuvoir, attention à ne pas attraper la crève"),
        ("Gelées", "Un froid glacial s'est abattu sur la région"),
        ("Froid intense, ciel dégagé", "Un froid intense s'est abattu sur la région. Heureusement le soleil pointe le bout de son nez"),
        ("Neige", "La neige tombe sur la région"),
        ("Gelées verglaçantes", "Un froid terrible s'est abattu sur la région. Les lacs et rivières sont gelés."),
        ("Pluies froides", "Un torrent de pluie glacé nous tombe dessus")
        ]

special = [
        ("Pied-de-vent", "Le temps est nuageux mais des rayons de lumière traversent le ciel"),
        ("Bourrasques (vent)", "Le temps est venteux et de violentes bourrasques soufflent parfois sur la région."),
        ("Brumes (Mod +1)", "Le temps est brumeux mais il reste possible de s'orienter. (Malus sur le déplacement)"),
        (u"Grèle (Mod +1)", "Une journée où la grèle tombe."),
        ("Orage (Mod +2)", "Orage et pluie ! Que du bonheur."),
        ("Brouillards épais (Mod +2)", "Un brouillard très épais est tombé sur la région. Attention à ne pas vous perdre (Malus sur le déplacement, risque de se retrouver sur le mauvais hexagone)"),
        (u"Rafales très violentes (Mod +3)", "Des rafales de vent violentes soufflent sur la région"), 
        (u"Poussières corrompues (vigueur contre poison) (Mod +4)", "Depuis la grande guerre contre le roi sorcier des vents empoisonnés soufflent de temps en temps sur l'empire. Les gens s'enferment chez eux dans ces cas et prient pour que le bétail et les récoltes ne succombent pas tous. (Jet de vigueur contre poison si vous sortez).")
        ]

def get_date(date):
    season = int(date["day"] / (6 * 3 * 5))
    month = int(date["day"] / (6 * 3))
    week = int(date["day"] / 6) % 3
    weekday = date["day"] % 6 

    msg = "*Jour %d, %s de %s (%s), %s %d*\n" % (
            weekday+1,
            weeks[week],
            months[month],
            seasons[season],
            date["ext"],
            date["year"],
            )
    current_weather = weather[date["weather"]][1]
    msg += "*Météo: %s*\n" % weather[date["weather"]][1]
    observation = "Observation possible"
    modif = 0
    if "pluie" in current_weather.lower():
        observation = "Observation impossible"
        modif += random.randint(1,3)
    if "neige" in current_weather.lower():
        observation = "Observation impossible"
        modif += random.randint(2,5)
    if "vent" in current_weather.lower():
        modif += random.randint(1,3)
    msg += "%s - Modif. péripétie et attaque à distance: %d\n" % (observation, date["weather_modif"])
    for event in date["events"]:
        ecart = event["date_record"] + event["duration"] - date["day"]
        if ecart > 0:
            msg += "%s (%d jours restants)\n" % (event["event"]+1, ecart)
        elif ecart == 0:
            msg += "%s (Dernier jour)\n" % event["event"]
        else:
            # Supprimer l'event
            pass 
    msg += get_hunger(date)
    return msg

def get_hunger(date):
    hunger = date["hunger"]
    if not hunger:
        msg = "Etat actuel: tout va bien - Nécessaire: rien\n"
    elif hunger == 1:
        msg = "Etat actuel: tout va bien - Nécessaire: 1 RU/pers sinon affaibli, pas de récupération de PV/mana, mort des blessés.\n"
    elif hunger == 2:
        msg = "Etat actuel: Affaibli, pas de récupération de PV, mort des blessés - Nécessaire: 1 RU/pers sinon affaibli & en danger, pas de récup de PV/mana, PV max divisé par 2, mort des blessés.\n"
    elif hunger == 3:
        msg = "Etat actuel: Affaibli & en danger, pas de récupération de PV, PV max divisé par 2, mort des blessés - Nécessaire: 1 RU/pers sinon affaibli & en danger, pas de récup de PV/mana, PV max divisé par 2, mort des blessés.\n"
    elif hunger == 4:
        msg = "Etat actuel: Affaibli & en danger, pas de récupération de PV, PV max divisé par 2, mort des blessés - Nécessaire: 1 RU/pers sinon mort.\n"
    elif hunger > 4:
        msg = "Etat actuel: Mort (sauf cas exceptionnel) - Nécessaire: 1 RU/pers\n"
    return msg

def roll_meteo(starter):
    if not starter and starter != 0:
        starter = random.randint(0,len(weather))
    new_weather = starter
    special = None
    res = random.randint(1,8)
    if res < 3:
        new_weather = starter + random.randint(-4,-1)
        special = None
    elif res > 5 and res < 8:
        new_weather = starter + random.randint(-4,-1)
        special = None
    elif res == 8:
        pass
        special = random.choice(["Pied-de-vent", "Bourrasques", "Brumes (Mod +1)", u"Grèle (Mod +1)", "Orage (Mod +2)", "Brouillards épais (Mod +2)", u"Rafales très violentes (Mod +3)", u"Poussières corrompues (vigueur contre poison) (Mod +4)"])
    modif = 0
    if "pluie" in weather[new_weather][0].lower():
        observation = "Observation impossible"
        modif += random.randint(1,3)
    if "neige" in weather[new_weather][0].lower():
        observation = "Observation impossible"
        modif += random.randint(2,5)
    if "vent" in weather[new_weather][0].lower():
        modif += random.randint(1,3)
    return new_weather, modif
