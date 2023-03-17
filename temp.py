    
    def eventually_check_MDP(self,S1) : 
        """ Model Checking du eventually pour une chaine de Markov avec action.
        
        Args
        ----
        S1 : list
            Liste des états qu'on cherche à atteindre
        """
        n_etat = len(self.liste_states) - len(S1) # On ne compte pas les états qu'on veut atteindre 
        n_action = [] # Nombre d'actions possibles pour chaque état
        
        for i in range(n_etat):
            n_action.append(len(self.states[self.liste_states[i]].transitions_with_action))
        
        n_tot_ligne = 0 
        for i in range(n_etat):
            if n_action[i] != 0:
                n_tot_ligne += n_action[i] + 2
            else:
                n_tot_ligne += 3
            
        # On crée la matrice A (avec n_etat colonnes et n_etat*(n_action+2) lignes)
        A = np.zeros((n_tot_ligne,n_etat))
        
        # On crée le vecteur b 
        b = np.zeros((n_tot_ligne,1))
        
        # On remplit la matrice A et le vecteur b

        # Pour chaque bloc de taille (n_action[i]+2) lignes et n_etat colonnes on remplit la matrice A 
        indice = 0
        for i in range(n_etat):
            etat_actif = self.states[self.liste_states[i]]
            # noms des actions possibles pour l'état i
            if n_action[i] != 0:
                for j in range(n_action[i]):
                    nom_action = list(etat_actif.transitions_with_action.keys())[j]
                    for k in range(n_etat):
                        etat_cible = self.states[self.liste_states[k]]
                        index_cible = -10
                        if etat_cible.state in etat_actif.transitions_with_action[nom_action]["targets"]:
                            index_cible = self.states[self.liste_states[i]].transitions_with_action[nom_action]["targets"].index(etat_cible.state)
                        if k == i:
                            if index_cible != -10:
                                A[indice+j,k] = 1 - self.states[self.liste_states[i]].transitions_with_action[nom_action]["weights"][index_cible]  / np.sum(self.states[self.liste_states[i]].transitions_with_action[nom_action]["weights"])
                            else:
                                A[indice+j,k] = 1
                        else:
                            if index_cible != -10:    
                                A[indice+j,k] = - self.states[self.liste_states[i]].transitions_with_action[nom_action]["weights"][index_cible]  / np.sum(self.states[self.liste_states[i]].transitions_with_action[nom_action]["weights"])
                            else:
                                A[indice+j,k] = 0
                for transitions in etat_actif.transitions_with_action[nom_action]["targets"]:
                    if transitions in S1:
                        index_cible = etat_actif.transitions_with_action[nom_action]["targets"].index(transitions)
                        b[indice+j] = self.states[self.liste_states[i]].transitions_with_action[nom_action]["weights"][index_cible]  / np.sum(self.states[self.liste_states[i]].transitions_with_action[nom_action]["weights"])
                indice += n_action[i]
                
            else:
                for j in range(1):
                    if j == 0:
                        for k in range(n_etat):
                            etat_cible = self.states[self.liste_states[k]]
                            index_cible = -10
                            if etat_cible.state in etat_actif.transitions_without_action["targets"]:
                                index_cible = self.states[self.liste_states[i]].transitions_without_action["targets"].index(etat_cible.state)
                            if k == i:
                                if index_cible != -10:
                                    A[indice+j,k] = 1 - self.states[self.liste_states[i]].transitions_without_action["weights"][index_cible]  / np.sum(self.states[self.liste_states[i]].transitions_without_action["weights"])
                                else:
                                    A[indice+j,k] = 1
                            else:
                                if index_cible != -10:    
                                    A[indice+j,k] = - self.states[self.liste_states[i]].transitions_without_action["weights"][index_cible]  / np.sum(self.states[self.liste_states[i]].transitions_without_action["weights"])
                                else:
                                    A[indice+j,k] = 0
                    for transitions in etat_actif.transitions_without_action["targets"]:
                        if transitions in S1:
                            index_cible = etat_actif.transitions_without_action["targets"].index(transitions)
                            b[indice+j] = self.states[self.liste_states[i]].transitions_without_action["weights"][index_cible]  / np.sum(self.states[self.liste_states[i]].transitions_without_action["weights"])
                indice += 1

            A[indice,i] = -1
            A[indice+1,i] = 1
            b[indice] = -1
            indice += 2
        A = -1*A
        b = -1*b
                    
        # On résout Ax>=b   avec comme fonction objectif (1,1,...,1)
        c = np.ones((n_etat,1))
        res = linprog(c, A_ub=A, b_ub=b, bounds=(None,None), method='simplex')
        print(f"Bravo ! L'algorithme converge ! La probabilité d'atteindre l'ensemble S1 à partir des autre sommets est : \n")
        liste_res = []
        for etat in self.liste_states:
            if etat not in S1:
                liste_res.append(etat)
        for etat in liste_res:
            print(f"Etat {etat} : {res.x[self.liste_states.index(etat)]}")

