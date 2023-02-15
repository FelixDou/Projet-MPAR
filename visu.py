# On affiche les données récupérées sous forme de graphique avec graphviz

import graphviz as gv

# On récupère les données
States = L['States']
Actions = L['Actions']
Transitions_with_action = L['Transitions_with_action']
Transitions_without_action = L['Transitions_without_action']

# On crée le graphique
G = gv.Digraph(format='png')

# On ajoute les états
for state in States:
    G.node(state)

# On ajoute les transitions sans action
for transition in Transitions_without_action:
    for i in range(len(Transitions_without_action[transition]['targets'])):
        G.edge(Transitions_without_action[transition]['from'],Transitions_without_action[transition]['targets'][i], label = str(Transitions_without_action[transition]['weights'][i])) 

# On ajoute les transitions avec action
for transition in Transitions_with_action:
    for i in range(len(Transitions_with_action[transition]['targets'])):
        G.edge(Transitions_with_action[transition]['from'],Transitions_with_action[transition]['targets'][i], label = str(Transitions_with_action[transition]['weights'][i]) + str(Transitions_with_action[transition]['action']))
# Creer une flèche par action 


G


