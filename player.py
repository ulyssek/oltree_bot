from config import *
import numpy as np

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
jobs = ["Archer","Assassin","Berzekr","Guerrier","Druide","Maître des bêtes"]
weapons = ["Arme","Arme bonus"]
armor = ["Armure","Bouclier"]

class Player:
    def __init__(self, name, skills):
        self.name = name
        self.skills = skills
        self.ace = [False, False, False]
        self.rolls = None
        self.jet = None
        self.init = None

    def skill_check(self,skill, rolls, ace):
        """Faire un test de vocation ou métier. Il est possible de préciser le type de jet ;bagarre type (soldat, voyageur, érudit, archer, assassin, berzekr, guerrier)"""
        self.jet = skill
        self.rolls = rolls
        self.ace = ace
        bonus_touch, bonus_dmg = self.get_bonus(skill)
        return self.format_bagarre(skill, rolls, bonus_touch, bonus_dmg)

    def get_bonus(self, jet):
        bonus_touch = 0
        bonus_dmg = 0
        if jet in vocations + jobs:
            if jet in vocations:
                bonus_touch = self.skills[jet]
            else:
                bonus_touch = self.skills["Soldat"]
                if jet == "Berzekr": # Bonus de berzekr + bonus de guerrier
                    bonus_touch += self.skills["Berzekr"]
                    bonus_dmg = self.skills["Berzekr"]
                    bonus_dmg += self.skills["Guerrier"]
                elif jet in ["Guerrier", "Archer"]:
                    bonus_dmg = self.skills[jet]
        elif jet == "Initiative":
            bonus_touch = self.skills["Soldat"]
        return bonus_touch, bonus_dmg

    def format_bagarre(self, jet, rolls, bonus_touch, bonus_dmg):
        rolls_txt = " ".join(map(lambda x : str(int(x)),rolls))
        mait, prou, exalt = map(lambda x: int(x), rolls)
        best_score = np.sum(np.sort(np.array((mait,prou,exalt)))[1:3])
        weapon = self.skills["Arme"]
        weapon_bonus = self.skills["Arme bonus"]
        if jet:
            if jet in vocations:
                msg = "**Jet de vocation (%s) de %s**\n" % (jet, self.name)
            elif jet == "Guerrier":
                msg = "**Jet de combat (%s) de %s**\n" % (jet, self.name)
            elif jet == "Berzekr":
                msg = "**Jet de combat (%s) de %s**. (Le bonus de guerrier est pris en compte).\n" % (jet, self.name)
            elif jet == "Archer":
                msg = "**Jet de combat (%s) de %s**.\n" %(jet, self.name) 
            elif jet == "Initiative":
                msg = "**Jet d'initiative de %s**\n" % (self.name)
            else:
                msg = "**Jet de machin de %s**. En vrai %s c'est pas parmi les trucs supportés donc va falloir appliquer les bonus à la main ou vérifier que tu aies pas écrit n'importe quoi. Bisous.\n" % (self.name, jet)
        else:
            msg = "Jet standard de %s\n" % self.name
        #Préciser l'arme utilisé
        if weapon:
            msg += "Arme (les dégâts à appliquer manuellement): %s\n" % weapons_dict[weapon]
        #Préciser les bonus de l'arme
        if weapon_bonus:
            msg += "Bonus arme (à appliquer): + %d dégâts\n" % int(weapon_bonus)
        msg += "Jet: %s (Bonus touche: %d, Bonus dégâts: %d)\n" % (rolls_txt, bonus_touch, bonus_dmg)
        #Préciser le résultat du jet (le meilleur est donné dans le cas d'un jet d'initiative
        if jet == "Initiative":
            msg += "Inititative de %s : %d\n\n\n" %(self.name,best_score+bonus_touch)
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

    def format_skills(self):
        """Affiche les statistiques"""
        msg = "**Compétences de %s" % self.name + "**"
        msg += "\n*CA*: %s *Mana*: %s *PV Max*: %s *Vigilance:* %s" % (10+sum(list(map(lambda x : self.skills[x],armor)))+int(self.skills["Guerrier"]/2),self.skills["DV"]*2+self.skills["Érudit"],self.skills["PV Max"],10+self.skills["Voyageur"]+int(self.skills["Assassin"]/2))
        msg += "\n**Vocations**\n"
        msg += " ".join(["%s : %s" % ("*"+vocation+"*",self.skills[vocation]) for vocation in vocations])
        msg += "\n**Métiers**\n"
        msg += " ".join(["%s : %s" % ("*"+job+"*",self.skills[job]) for job in jobs if str(self.skills[job])!='0'])
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
