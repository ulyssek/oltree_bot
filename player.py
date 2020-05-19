from config import *
from timeline import *
import numpy as np

weapons_close = {
        "1h_sword": "Epée",
        "2h_sword": "Epée à deux mains (+2 dégâts)",
        "1h_axe": "Hache (-1 à l'attaque contre combattants armés, +2 dégâts contre monstres",
        "2h_axe": "Hache à deux mains (-1 à l'attaque contre combattants armés, +4 dégâts contre monstres, +2 dégâts contre les autres)",
        "spear": "Lance deux mains (+1 CA contre adversaires sans boucliers, +2 dégâts contre des grandes créatures ou cavaliers)",
        "dagger": "Dague (-2 CA contre adversaires avec arme plus longue, pas de malus en milieu confiné)",
        }
weapons_distance = {
        "longbow": "Arc long",
        "shortbow": "Arc court",
        }

prouesse= [
        ("Effet temporaire sur ennemi (en danger, affaiblir, à terre, contraint), il peut faire un jet de sauvegarde OU annuler un effet sur un allié.", "Influencer fortement l’attitude des figurants présents, inventer un élément du décor qui change la situation de manière importante."),
        ("Bonus +1d8 au dé de maîtrise. Saisir un adversaire plus grand.", "Énoncer un fait qui se vérifie (à la discrétion du meneur de jeu qui peut le modifier légèrement pour coller à l’histoire), jouer une carte d’exaltation au nom d’un allié."),
        ("Changer conditions générales (désarmer adversaire, trouver un abri, gagner un bonus de +2 à CA/classe d'armure). Avantage dure jusqu'à la fin de la scène.", "Ajouter un élément pertinent au décor ou à l'histoire"),
        ("Bonus de +2 à un jet futur (soi ou allié). Saisir un adversaire de sa taille","Ajouter un élément mineur au décor ou influence légèrement l'attitude générale")]

weapons = dict(weapons_close)
weapons.update(weapons_distance)

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

vocations = ["Soldat","Voyageur","Érudit"]
jobs_dict = {
        "Druide":"Érudit",
        "Maître des bêtes":"Voyageur",
        "Marchand":"Voyageur",
        "Noble":"Voyageur",
        "R\u00f4deur":"Voyageur",
        "Berzekr":"Soldat",
        "Archer":"Soldat",
        "Assassin":"Soldat",
        "Guerrier":"Soldat",
    }
jobs_other = [x for x in jobs_dict.keys() if jobs_dict[x] != "Soldat"]
jobs_fight = [x for x in jobs_dict.keys() if jobs_dict[x] == "Soldat"]

sauvegarde = {
        "Réflexe":"Voyageur",
        "Vigueur":"Soldat",
        "Volonté":"Érudit"}
jobs = jobs_other + jobs_fight

weapons = ["Arme","Arme bonus"]
armor = ["Armure","Bouclier"]

status = ["En danger", "Affaibli", "Contraint"]

def fix_skill(skill):
    """Corrige le skill passé pour pallier aux erreurs de frappe"""
    if type(skill) == str:
        skill = skill.capitalize() 
        if skill in ["Erudit"]:
            skill = "Érudit"
        elif skill in ["Berzerk", "Berzeker"]:
            skill = "Berzekr"
        elif skill in ["Assasin", "Asassin"]:
            skill = "Assassin"
    return skill

class Player:
    def __init__(self, name, skills, timeline):
        self.name = name
        self.skills = skills
        self.ace = [False, False, False]
        self.rolls = None
        self.jet = None
        self.init = None
        self.params = None
        self.timeline = timeline

    def change_pv(self, value):
        if value < 0:
            self.skills["PV"] = max(0, self.skills["PV"] + value)
        if value > 0:
            self.skills["PV"] = min(self.skills["PV"] + value, self.skills["PV Max"])

    def format_pv(self):
        return "**PV**: %d/%d" % (self.skills["PV"], self.skills["PV Max"])

    def skill_check(self,skill, rolls, ace, params=None):
        """Faire un test de vocation ou métier. Il est possible de préciser le type de jet ;bagarre type (soldat, voyageur, érudit, archer, assassin, berzekr, guerrier)"""
        self.jet = fix_skill(skill)
        self.rolls = rolls
        self.params = params
        self.ace = ace
        bonus_touch, bonus_dmg = self.get_bonus(skill)
        return self.format_bagarre(skill, rolls, bonus_touch, bonus_dmg)

    def get_bonus_skills(self, jet):
        bonus_touch = 0
        bonus_dmg = 0
        if jet in vocations:
            bonus_touch = self.skills[jet]
        elif jet in list(sauvegarde.keys()):
            bonus_touch = self.skills[sauvegarde[jet]]
        elif jet in jobs:
            bonus_touch = self.skills[jobs_dict[jet]]
            if jet in ("Guerrier","Archer"):
                bonus_dmg = self.skills[jet]
            elif jet == "Berzekr": # Bonus de berzekr + bonus de guerrier
                bonus_touch += self.skills["Berzekr"]
                bonus_dmg = self.skills["Guerrier"]
                bonus_dmg += self.skills["Berzekr"]
            elif jet == "Noble": #Bonus de Noble + bonus de marchand
                bonus_touch += self.skills["Marchand"]
                bonus_touch += self.skills["Noble"]
                bonus_dmg += self.skills["Noble"]
                bonus_dmg += self.skills["Marchand"]
            else:
                bonus_touch += self.skills[jet]
                bonus_dmg += self.skills[jet]
        elif jet == "Initiative":
            bonus_touch = self.skills["Soldat"]
        return bonus_touch, bonus_dmg

    def get_bonus_weapon(self, jet):
        bonus_touch, bonus_dmg = 0, 0
        # Jet d'archer et arme est un arc
        if jet == "Archer" and self.skills["Arme"] in weapons_distance.keys():
            bonus_dmg += self.skills["Arme bonus"]
            bonus_touch += self.skills["Arme bonus"]
        # Jet de guerrier ou berzekr et arme est une arme de cac
        elif jet in ["Berzekr", "Guerrier"] and self.skills["Arme"] in weapons_close.keys():
            bonus_dmg += self.skills["Arme bonus"]
            bonus_touch += self.skills["Arme bonus"]
            if "2h" in self.skills["Arme"]:
                bonus_dmg += 2
            if "axe" in self.skills["Arme"]:
                if "armed" in self.params:
                    bonus_touch += -1
                if "monster" in self.params:
                    bonus_dmg += 2

        return bonus_touch, bonus_dmg

    def get_bonus_weather(self, jet):
        if jet in ["Archer"] and "meteo" in self.params:
            return -self.timeline["weather_modif"], -self.timeline["weather_modif"]
        else:
            return 0, 0

    def get_bonus(self, jet):
        bonus_touch, bonus_dmg = tuple(map(sum, zip(
            self.get_bonus_skills(jet),
            self.get_bonus_weapon(jet),
            self.get_bonus_weather(jet),
            )))
        return bonus_touch, bonus_dmg

    def format_bonus_weapon(self, jet):
        """Renvoie le bonus d'arme formaté. Si le jet ne correspond pas à du combat renvoie une chaine vide"""
        msg = ""
        if jet in ["Soldat"] + jobs_fight:
            weapon = self.skills["Arme"]
            weapon_bonus = self.skills["Arme bonus"]
            #Préciser l'arme utilisée
            if weapon and ("monster" in self.params or "armed" in self.params):
                msg += "Arme (déjà appliqué): %s\n" % weapons_dict[weapon]
            elif weapon:
                msg += "Arme (à appliquer): %s\n" % weapons_dict[weapon]
            # Si l'arme a des bonus
            if weapon_bonus:
                msg += "Bonus arme (déjà appliqué): + %d\n" % int(weapon_bonus)

        return msg

    def format_bonus_weather(self, jet):
        if jet in ["Archer"]:
            if "meteo" in self.params:
                return "Modificateur météo: -%d (appliqué)\n" % self.timeline["weather_modif"]
            if "meteo" not in self.params:
                return "Modificateur météo: -%d (à appliquer)\n" % self.timeline["weather_modif"]
        else:
            return ""

    def format_bagarre(self, jet, rolls, bonus_touch, bonus_dmg):
        rolls_txt = " ".join(map(lambda x : str(int(x)),rolls))
        mait, prou, exalt = map(lambda x: int(x), rolls)
        best_score = np.sum(np.sort(np.array((mait,prou,exalt)))[1:3])

        if jet:
            if jet in vocations:
                msg = "**Jet de vocation (%s) de %s**\n" % (jet, self.name)
            elif jet in sauvegarde.keys():
                msg = "**Jet de sauvegarde (%s) de %s**\n" % (jet, self.name)
            elif jet == "Guerrier":
                msg = "**Jet de combat (%s) de %s**\n" % (jet, self.name)
            elif jet == "Berzekr":
                msg = "**Jet de combat (%s) de %s**. (Le bonus de guerrier est pris en compte).\n" % (jet, self.name)
            elif jet == "Archer":
                msg = "**Jet de combat (%s) de %s**.\n" %(jet, self.name) 
            elif jet in jobs:
                msg = "**Jet de métier (%s) de %s**. \n" %(jet, self.name)
            elif jet == "Initiative":
                msg = "**Jet d'initiative de %s**\n" % (self.name)
            else:
                msg = "**Jet de machin de %s**. En vrai %s c'est pas parmi les trucs supportés donc va falloir appliquer les bonus à la main ou vérifier que tu aies pas écrit n'importe quoi. Bisous.\n" % (self.name, jet)
        else:
            msg = "Jet standard de %s\n" % self.name
        msg += self.format_bonus_weapon(jet)
        msg += self.format_bonus_weather(jet)
        msg += "Jet: %s (Bonus touche: %d, Bonus dégâts: %d)\n" % (rolls_txt, bonus_touch, bonus_dmg)
        #Préciser le résultat du jet (le meilleur est donné dans le cas d'un jet d'initiative
        if jet == "Initiative":
            msg += "Inititative de %s : %d\n\n" %(self.name,best_score+bonus_touch)
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
        return msg, best_score
    
    def change_status(self, param):
        """Change le status"""
        self.skills[param] = not self.skills[param]

    def format_skills(self):
        """Affiche les statistiques"""
        msg = "**Compétences de %s" % self.name + "**"
        msg += "\n*CA*: %s *Mana*: %s *PV*: %d/%d *Vigilance:* %s" % (
                10+sum(list(map(lambda x : self.skills[x],armor)))+int(self.skills["Guerrier"]/2),
                self.skills["DV"]*2+self.skills["Érudit"],
                self.skills["PV"],
                self.skills["PV Max"],
                10+self.skills["Voyageur"]+int(self.skills["Assassin"]/2)
                )
        _ = ", ".join([_ for _ in status if self.skills[_]])
        if _:
            msg += "\n*Status*: %s" % _
        msg += "\n**Vocations**\n"
        msg += " ".join(["%s : %s" % ("*"+vocation+"*",self.skills[vocation]) for vocation in vocations])
        msg += "\n**Métiers civils**\n"
        temp = ["%s : %s" % ("*"+job+"*",self.skills[job]) for job in jobs_other if str(self.skills[job])!='0']
        if temp == []:
            msg += "Nada"
        else:
            msg += " ".join(temp)
        msg += "\n**Métiers bagarre**\n"
        temp = ["%s : %s" % ("*"+job+"*",self.skills[job]) for job in jobs_fight if str(self.skills[job])!='0']
        if temp == []:
            msg += "Nada"
        else:
            msg += " ".join(temp)
        msg += "\n**Armes**\n"
        temp = ["%s : %s" % ("*"+weapon+"*",self.skills[weapon]) for weapon in weapons if str(self.skills[weapon])!='0']
        if temp == []:
            msg += "Nada"
        else:
            msg += " ".join(temp)
        msg += "\n**Armures**\n"
        temp = ["%s : %s" % ("*"+armor+"*",self.skills[armor]) for armor in armor if str(self.skills[armor])!='0']
        if temp == []:
            msg += "Nada"
        else:
            msg += " ".join(temp)
        return msg
