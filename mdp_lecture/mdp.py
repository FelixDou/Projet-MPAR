from antlr4 import *
from gramLexer import gramLexer
from gramListener import gramListener
from gramParser import gramParser
import sys
import pickle

# On crée un dictionnaire pour stocker les informations du fichier mdp
test_liste = {'States':[],'Actions':[],'Transitions_with_action':{},'Transitions_without_action':{}, 'Rewards':{}}
# la valeur de number_of_transitions est incrémentée à chaque transition afin de pouvoir créer des clés différentes pour chaque transition
number_of_transitions = 0
        
class gramPrintListener(gramListener):

    def __init__(self):
        pass
        
    def enterStatenoreward(self, ctx):
        states = [str(x) for x in ctx.ID()]
        # On ajoute les états dans le dictionnaire
        test_liste["States"] = states
        print("States: %s" % states)

    def enterStatereward(self, ctx):
        states = [str(x) for x in ctx.ID()]
        rewards = [int(str(x)) for x in ctx.INT()]
        for states,rewards in zip(states,rewards):
            # On ajoute les états et les récompenses dans le dictionnaire
            test_liste["States"].append(states)
            test_liste["Rewards"][states] =rewards
        # On ajoute les états dans le dictionnaire
        print("States: %s" % test_liste["States"])

    def enterDefactions(self, ctx):
        actions = [str(x) for x in ctx.ID()]
        # On ajoute les actions dans le dictionnaire
        test_liste["Actions"] = actions
        print("Actions: %s" % actions)

    def enterTransact(self, ctx):
        global test_liste
        global number_of_transitions
        ids = [str(x) for x in ctx.ID()]
        dep = ids.pop(0)
        act = ids.pop(0)
        weights = [int(str(x)) for x in ctx.INT()]
        # On ajoute toutes les informations de la transition dans le dictionnaire
        test_liste["Transitions_with_action"][number_of_transitions] = {"from" : dep, "action" : act, "targets" : ids, "weights" : weights}
        number_of_transitions += 1
        print("Transition from " + dep + " with action "+ act + " and targets " + str(ids) + " with weights " + str(weights))
        
    def enterTransnoact(self, ctx):
        global test_liste
        global number_of_transitions
        ids = [str(x) for x in ctx.ID()]
        dep = ids.pop(0)
        weights = [int(str(x)) for x in ctx.INT()]
        # On ajoute toutes les informations de la transition dans le dictionnaire
        test_liste["Transitions_without_action"][number_of_transitions] = {"from" : dep, "targets" : ids, "weights" : weights}
        number_of_transitions += 1
        print("Transition from " + dep + " with no action and targets " + str(ids) + " with weights " + str(weights))



# On récupère les listes en les enregistrant dans un fichier pickle
# write list to binary file
def write_list(liste,nom_fichier):
    # store list in binary file so 'wb' mode
    with open(nom_fichier, 'wb') as fp:
        pickle.dump(liste, fp)


def main():
    lexer = gramLexer(StdinStream())
    stream = CommonTokenStream(lexer)
    parser = gramParser(stream)
    tree = parser.program()
    printer = gramPrintListener()
    walker = ParseTreeWalker()
    walker.walk(printer, tree)
    print(test_liste)
    write_list(test_liste,"liste_donnees")

if __name__ == '__main__':
    main()


# commande python ./mdp.py < ./ex.mdp
