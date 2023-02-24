import mdp
import pickle
import numpy as np
import random

mdp.main() # On exécute le programme mdp.py


# On lit le .pickle des données que l'on souhaitent récupérer

# Read list to memory
def read_list(nom_liste):
    # for reading also binary mode is important
    with open(nom_liste, 'rb') as fp:
        liste = pickle.load(fp)
        return liste

L = read_list("liste_donnees")
print('Données récupérées', L)

print('States:', L['States'])
print('Actions:', L['Actions'])
for transitions in L['Transitions_with_action']:
    print('Transition with action' ':', L['Transitions_with_action'][transitions])
for transitions in L['Transitions_without_action']:
    print('Transition without action' ':', L['Transitions_without_action'][transitions])



class States():
    def __init__(self, state, id,transitions_with_action, transitions_without_action):
        """
        Initialisation des états de la chaine de markov
        
        Args
        ----
        state : str
            Nom de l'état (S0...)
        id : int
            Numéro de l'état
        transitions_with_action : dict
            Dictionnaire de l'ensemble des transitions avec action
        transitions_without_action : dict
            Dictionnaire de l'ensemble des transitions sans action
        """
        self.state = state
        self.id = id
        self.transitions_without_action = {}
        self.transitions_with_action = {}

        sans_action = True # on crée ce booléen pour vérifier qu'il n'y a pas de transition avec action ensuite
        for transition in transitions_without_action:
            # on parcours l'ensemble des transitions
            transi_active = transitions_without_action[transition]
            if transi_active["from"]==self.state: # on vérifie si l'état de départ est l'état actif
                sans_action = False
                self.transitions_without_action["targets"] = transi_active["targets"]
                self.transitions_without_action["weights"] = transi_active["weights"]

        for transition in transitions_with_action:
            transi_active = transitions_with_action[transition]
            if transi_active["from"]==self.state and sans_action == True:
                # les clés dans transition_with_action sont les actions et les valeurs des dict des états cibles et leurs poids
                self.transitions_with_action[transi_active["action"]] = {"targets" : transi_active["targets"], "weights" : transi_active["weights"]}
            elif transi_active["from"]==self.state and sans_action == False:
                print("\nWarning : l'état", self.state, "comporte des transitions avec et sans action")
                print("Il est donc impossible de déterminer la transition à effectuer, il faut revoir la modélisation \n")
                break

    def __repr__(self):
        return (f"State : {self.state} \n State id {self.id} \n Transitions without action : {self.transitions_without_action} \n Transitions with action : {self.transitions_with_action}")


class markov():
    def __init__(self, states, actions, transitions_with_action, transitions_without_action):
        """
        Initialisation de la chaine de markov

        Args
        ----
        states : list
            Liste des états de la chaine
        actions : list
            Liste des actions possibles
        transitions_with_action : dict
            Dictionnaire de l'ensemble des transitions avec action
        transitions_without_action : dict
            Dictionnaire de l'ensemble des transitions sans action
        """
        self.states = {}
        self.liste_states = states
        self.actions = actions
        self.transitions_with_action = transitions_with_action
        self.transitions_without_action = transitions_without_action

        for state in states:
            self.states[f"{state}"] = States(state, states.index(state), transitions_with_action, transitions_without_action)
        
        markov.parsing(self, states) # on vérifie qu'on a pas de problèmes de parsing
        
    def parsing(self, states):
        """
        On réalise différents tests pour vérifier que la chaine de markov (ou la MDP) est correctement définie

        Args
        ----
        states : list
            Liste des états de la chaines (avec possiblement des doublons)
        """
        # On concatène les transitions avec et sans action pour plus de simplicité pour les test
        all_transitions = []
        transitions_without_action = []
        transitions_with_action = []
        for elem in self.transitions_without_action:
            transitions_without_action.append(self.transitions_without_action[elem])
            all_transitions.append(self.transitions_without_action[elem])
        for elem in self.transitions_with_action:
            transitions_with_action.append(self.transitions_with_action[elem])
            all_transitions.append(self.transitions_with_action[elem])

        # On vérifie que les états déclarés sont utilisés
        used_states = []
        for transitions in all_transitions:
            used_states.append(transitions["from"])
            used_states.append(transitions["targets"])
        for state in self.states:
            if state not in used_states:
                print(f"Warning : l'état {state} est déclaré mais n'est pas utilisé")

        # On vérifie qu'un état n'est pas déclaré plusieurs fois
        if len(states) != len(self.states): # self.states supprime automatiquement les doublons
            print("Warning : un état est déclaré plusieurs fois")

        # On vérifie que les actions ne sont pas déclarées plusieurs fois
        actions_uniques = set(self.actions)
        if len(actions_uniques) != len(self.actions):
            print("Warning : une action est déclarée plusieurs fois")
    
        # On vérifie qu'un état utilisé dans des transitions est déclaré
        for transitions in all_transitions:
            if transitions["from"] not in self.states:
                print(f"Warning : l'état {transitions['from']} est utilisé dans une transition mais n'est pas déclaré")
            for target in transitions["targets"]:
                if target not in self.states:
                    print(f"Warning : l'état {target} est utilisé dans une transition mais n'est pas déclaré")
        
        # On vérifie qu'une action déclarée est utilisée
        actions_utilisés = []
        for transitions in transitions_with_action:
            actions_utilisés.append(transitions["action"])
        actions_utilisés = set(actions_utilisés) # on enlève les doublons
        if len(actions_utilisés) != len(self.actions):
            print("Warning : une action est déclarée mais n'est pas utilisée")

        # On vérifie que les actions utilisées sont déclarées
        for action in actions_utilisés:
            if action not in self.actions:
                print(f"Warning : l'action {action} est utilisée mais n'est pas déclarée")

    def parcours(self,N, without_action = False, positionnel = False): # on parcours la chaine (en faisant N étapes)
        """ 
        On parcours la chaine en faisant N étapes
        
        Args
        ----
        N : int
            Nombre d'étapes
        without_action : bool
            Si on fait des transitions sans action
        with_action : bool
            Si on fait des transitions en prenant en compte celels avec action
        """
        etat_initial = self.liste_states[0] #état initial : premier élément
        etat_actif = self.states[etat_initial] # on prend l'objet correspondant à l'état initial

        if without_action:
            for i in range(N):
                print(etat_actif.state) # on affiche l'état en cours
                poids = etat_actif.transitions_without_action["weights"]
                poids_total = np.sum(poids)
                poids = poids/poids_total # on normalise les poids pour qu'ils soient entre 0 et 1
                poids = np.cumsum(poids) # on fait la somme cumulée des poids, afin de pouvoir faire un tirage aléatoire (il ne faut pas que par exemple les deux probas soient de 0.5, il en faut une de 0.5 et l'autre de 1)

                choix = random.random() # tirage aléatoire entre 0 et 1

                for j in range(len(poids)): # on recherche l'état cible
                    if choix <= poids[j]:
                        etat_actif = self.states[etat_actif.transitions_without_action["targets"][j]]
                        break

        elif positionnel == True : # adversaire positionnel
            print("Choix d'un adversaire positionnel")
            adv_pos = {} # contient pour chaque état, le choix de l'adversaire
            for state in self.liste_states :
                etat = self.states[state]
                if etat.transitions_with_action != {} : # si l'état possèdes des transitions avec actions
                    print(f"choix possibles pour l'état {state}:")
                    print(etat.transitions_with_action.keys())
                    print(f"choix de l'action pour l'état {state}:")
                    action = input()
                    print(action)
                    adv_pos[state] = action
            print(adv_pos)
            for i in range(N):
                print(etat_actif.state) # on affiche l'état en cours
                if etat_actif.transitions_with_action == {} : # si l'état n'a pas de transitions avec actions :
                    poids = etat_actif.transitions_without_action["weights"]

                    poids_total = np.sum(poids)
                    poids = poids/poids_total # on normalise les poids pour qu'ils soient entre 0 et 1
                    poids = np.cumsum(poids) # on fait la somme cumulée des poids, afin de pouvoir faire un tirage aléatoire (il ne faut pas que par exemple les deux probas soient de 0.5, il en faut une de 0.5 et l'autre de 1)

                    choix = random.random() # tirage aléatoire entre 0 et 1

                    for j in range(len(poids)): # on recherche l'état cible
                        if choix <= poids[j]:
                            etat_actif = self.states[etat_actif.transitions_without_action["targets"][j]]
                            break
                else :
                    action_choisie = adv_pos[etat_actif.state]
                    print(f"Action choisie : {action_choisie}")
                    poids = etat_actif.transitions_with_action[action_choisie]["weights"] # on ne prend que les poids de l'action choisie par l'adversaire
                    poids_total = np.sum(poids)
                    poids = poids/poids_total # on normalise les poids pour qu'ils soient entre 0 et 1
                    poids = np.cumsum(poids) # on fait la somme cumulée des poids, afin de pouvoir faire un tirage aléatoire (il ne faut pas que par exemple les deux probas soient de 0.5, il en faut une de 0.5 et l'autre de 1)

                    choix = random.random() # tirage aléatoire entre 0 et 1

                    for j in range(len(poids)): # on recherche l'état cible
                        if choix <= poids[j]:
                            etat_actif = self.states[etat_actif.transitions_with_action[action_choisie]["targets"][j]]
                            break



    def __repr__(self):
        return (f"States : {self.states} \n Actions : {self.actions}")
    

import graphviz as gv
def afficher(L, etat = "default"):
    """Fonction qui permet de représenter le graphe de la chaine de Markov avec ou sans action. Dans le mode "default", le graphe de base est affiché.
    Dans le mode "etat", on peut choisir un état et il sera mis en évidence en étant de couleur bleue.
    """
    # On récupère les données
    States = L['States']
    Actions = L['Actions']
    Transitions_with_action = L['Transitions_with_action']
    Transitions_without_action = L['Transitions_without_action']

    # On crée le graphique
    G = gv.Digraph(format='png')

    if etat == "default":
        for state in States:
            G.node(state)
    else:
        for state in States:
            if state == etat:
                G.node(state, color = 'blue', style = 'filled')
            else:
                G.node(state)
    
    #On ajoute les actions
    for actions in Actions:
        G.node(actions, shape = 'point')
        
    for transition in Transitions_with_action:
        G.edge(Transitions_with_action[transition]['from'], Transitions_with_action[transition]['action'], label=str(Transitions_with_action[transition]['action']), color = 'red')
    

    # On ajoute les transitions sans action
    for transition in Transitions_without_action:
        for i in range(len(Transitions_without_action[transition]['targets'])):
            G.edge(Transitions_without_action[transition]['from'],Transitions_without_action[transition]['targets'][i], label = str(Transitions_without_action[transition]['weights'][i])) 

    # On ajoute les transitions avec action
    for transition in Transitions_with_action:
        for i in range(len(Transitions_with_action[transition]['targets'])):
            G.edge(Transitions_with_action[transition]['action'],Transitions_with_action[transition]['targets'][i], label = str(Transitions_with_action[transition]['weights'][i]))
    
    return G

import numpy as np
import imageio
import os

def simulation(L, n_iter, initial_state= "S0", mode_adv = "random" ):
    """ Fonction qui permet de simuler une chaine de Markov avec ou sans action. On peut choisir le nombre d'itération, l'état initial et le mode de l'adversaire.
    Pour l'instant, seul le mode "random" est disponible."""
    current_state = initial_state
    States = L['States']
    Actions = L['Actions']
    Transitions_with_action = L['Transitions_with_action']
    Transitions_without_action = L['Transitions_without_action']
    G = afficher(L, etat = current_state)
    G.render('image0')
    images = []
    if mode_adv == "random":
        for i in range(n_iter):
                actions_possibles = []
                for transitions in Transitions_with_action:
                    if Transitions_with_action[transitions]['from'] == current_state:
                        actions_possibles.append(Transitions_with_action[transitions]['action'])
                if len(actions_possibles) == 0:
                    for transitions in Transitions_without_action:
                        if Transitions_without_action[transitions]['from'] == current_state:
                            poids = Transitions_without_action[transitions]['weights']
                            poids_total = np.sum(poids)
                            poids = poids/poids_total
                            poids = np.cumsum(poids)
                            choix = random.random()
                            for j in range(len(poids)):
                                if choix <= poids[j]:
                                    current_state = Transitions_without_action[transitions]['targets'][j]
                                    break
                else:
                    action_choisie = random.choice(actions_possibles)
                    for transitions in Transitions_with_action:
                        if Transitions_with_action[transitions]['action'] == action_choisie:
                            poids = Transitions_with_action[transitions]['weights']
                            poids_total = np.sum(poids)
                            poids = poids/poids_total
                            poids = np.cumsum(poids)
                            choix = random.random()
                            for j in range(len(poids)):
                                if choix <= poids[j]:
                                    current_state = Transitions_with_action[transitions]['targets'][j]
                                    break
                                
                G = afficher(L, etat = current_state)
                G.render('image'+str(i+1))
                images.append(imageio.imread('image'+str(i+1)+'.png'))
    imageio.mimsave('simulation.gif', images,fps=3)
    for i in range(n_iter):
        os.remove('image'+str(i)+'.png')
    return current_state
    

if __name__ == "__main__":
    # States(L['States'][1], 0, L['Transitions_with_action'], L['Transitions_without_action'])

    M = markov(L['States'], L['Actions'], L['Transitions_with_action'], L['Transitions_without_action'])

    # M.parcours(10, without_action = True)
    M.parcours(10,positionnel=True)
