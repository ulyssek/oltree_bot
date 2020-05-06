from config import *

class Player:
    def __init__(self, name, skills):
        self.name = name
        self.skills = skills

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

