# -*- coding: utf-8 -*-
from copy import deepcopy
import sys

# -*- coding: utf-8 -*-
# ---Encoding/decoding---#

def encodeLab(tab):
    lab = {}
    for i in range(len(tab)):
        for j in range(len(tab[i])):
            lab[(i, j)] = []
            l = lab[(i, j)]
            if 'h' in tab[i][j]:
                l += [(i-1, j)]
            if 'd' in tab[i][j]:
                l += [(i, j+1)]
            if 'b' in tab[i][j]:
                l += [(i+1, j)]
            if 'g' in tab[i][j]:
                l += [(i, j-1)]
    lab["nlines"] = len(tab)
    lab["ncolumns"] = len(tab[0])
    return lab


def decodeLab(lab):    
    tab = [["" for j in range(lab["ncolumns"])] for i in range(lab["nlines"])]
    for i in range(len(t)):
        for j in range(len(t[i])):
            if (i-1, j) in lab[(i, j)]:
                tab[i][j] += 'h'
            if (i, j+1) in lab[(i, j)]:
                tab[i][j] += 'd'
            if (i+1, j) in lab[(i, j)]:
                tab[i][j] += 'b'
            if (i, j-1) in lab[(i, j)]:
                tab[i][j] += 'g'
    return t


def nb_murs(lab):
    n = lab["nlines"]
    m = lab["ncolumns"]
    murs_max = n*(m-1) + m*(n-1)
    non_murs = []
    for k in lab.keys():
        if type(k)==str:
            continue
        for connect in lab[k]:
            if [connect,k] in non_murs:
                continue
            non_murs.append([k,connect])
    return murs_max - len(non_murs)



# ---Misc---#

def adjacent(cell, size=None): #size = [nlines, ncolumns] pour éviter de renvoyer des cellules hors labyrinthe
    if size==None:
        return [
            (cell[0]-1, cell[1]  ),
            (cell[0]  , cell[1]-1),
            (cell[0]+1, cell[1]  ),
            (cell[0]  , cell[1]+1)
        ]
    return [adj for adj in adjacent(cell) if (adj[0]>=0 and adj[0]<size[0] and adj[1]>=0 and adj[1]<size[1])]

def get_cell_occurence(lab, cell=(0, 0), previous=None, markList=None):
    if markList == None:
        markList = [[0 for j in range(lab["ncolumns"])] for i in range(lab["nlines"])]
    y, x = cell[0], cell[1]
    markList[y][x]+=1
    if markList[y][x] >= 2:
        return markList
    for adj in adjacent(cell):
        if adj in lab[cell] and adj != previous:
            markList = get_cell_occurence(lab, cell = adj, previous = cell, markList=markList)
    return markList

def merge_labs(lab1, lab2):
    lab = {}

    lab["ncolumns"] = max(lab1["ncolumns"], lab2["ncolumns"])
    lab["nlines"] = max(lab1["nlines"], lab2["nlines"])

    for y in range(lab["nlines"]):
        for x in range(lab["ncolumns"]):
            lab[(y, x)] = []
            if (y, x) in lab1.keys():
                for cell in lab1[(y, x)]:
                    if cell in lab2[(y, x)]:
                        lab[(y, x)].append(cell)
            if (y, x) in lab2.keys():
                for cell in lab2[(y, x)]:
                    if cell in lab1[(y, x)] and cell not in lab[(y, x)]:
                        lab[(y, x)].append(cell)
    return lab

def reverse_lab(lab):
    for key in lab.keys():
        if type(key) == type("a"):
            continue
        l = []
        for cell in adjacent(key, size=[lab["nlines"], lab["ncolumns"]]):
            if cell not in lab[key]:
                l.append(cell)
        lab[key] = l
    return lab

def empty_lab(n, m):
    lab = {"nlines":m, "ncolumns":n}
    for x in range(n):
        for y in range(m):
            lab[(y, x)] = []
    return lab

def canonical_lab(n, m):
    lab = {"nlines":m, "ncolumns":n}
    y, x = 0, 0
    direction = 1
    lab[(y, x)] = []
    while True:
        if 0 <= y+direction and y+direction < m:
            lab[(y, x)].append((y+direction, x))
            lab[(y+direction, x)] = [(y, x)]
            y += direction
        elif x < n-1:
            lab[(y, x)].append((y, x+1))
            lab[(y, x+1)] = [(y, x)]
            direction = -direction
            x += 1
        else:
            break
    return lab

def get_deadends(lab):
    deadends = []
    for cell in lab.keys():
        if type(cell) != type("a"):
            if len(lab[cell]) == 1 and cell != (0, 0):
                deadends.append(cell)
    return deadends

def lab_equality(lab1, lab2):
    if lab1["ncolumns"] != lab1["ncolumns"] or lab1["nlines"] != lab2["nlines"]:
        return False
    return all(set(lab1[cell]) == set(lab2[cell]) for cell in lab1.keys() if type(cell) != type("a"))


# ---Check---#

def is_well_defined(lab):
    keys = lab.keys()

    ymax, xmax = 0, 0
    for key in keys:
        if type(key) == type("a"):
            continue
        if key[0] > ymax: ymax=key[0]
        if key[1] > xmax: xmax=key[1]
        for cell in lab[key]:
            if key not in lab[cell]:
                return False

    if lab["ncolumns"] != xmax+1 or lab["nlines"] != ymax+1:
        return False

    for y in range(lab["nlines"]):
        for x in range(lab["ncolumns"]):
            if (y, x) not in keys:
                return False

    return True

def is_true_lab(lab):
    for line in get_cell_occurence(lab):
        for cell in line:
            if cell !=1:
                return False
    return True


# ---Generation pseudo-lab---#

def get_bin_list(n, nmax):
    if n == 0:
        return [0 for _ in range(len(bin(nmax))-3)]
    n = bin(n)
    digits = []
    for i in range(len(n)-2):
        digits.append(int(n[i+2]))
    while len(digits) < len(bin(nmax))-3:
        digits.insert(0,0)
    return digits

            

def generate_pseudo_lab(ncolumns, nlines):
    nb_ver_walls = 2 ** ((ncolumns-1)*nlines)
    nb_hor_walls = 2 ** (nlines*(ncolumns-1))
    
    ver_labs = []
    for n in range(nb_ver_walls):
        lab = {"nlines":nlines, "ncolumns":ncolumns}
        nbin = get_bin_list(n, nb_ver_walls)
        for i in range(len(nbin)):
            y = i//(ncolumns-1)
            x = i%(ncolumns-1)
            if nbin[i]:
                if (y, x) not in lab.keys():
                    lab[(y, x)] = [(y, x+1)]
                else:
                    lab[(y, x)].append((y, x+1))
                if (y, x+1) not in lab.keys():
                    lab[(y, x+1)] = [(y, x)]
                else:
                    lab[(y, x+1)].append((y, x))
            else:
                if (y, x) not in lab.keys():
                    lab[(y, x)] = []
                if (y, x+1) not in lab.keys():
                    lab[(y, x+1)] = []
        ver_labs.append(reverse_lab(lab))
    
    hor_labs = []
    for n in range(nb_hor_walls):
        lab = {"nlines":nlines, "ncolumns":ncolumns}
        nbin = get_bin_list(n, nb_hor_walls)
        for i in range(len(nbin)):
            y = i//(ncolumns)
            x = i%(ncolumns)
            if nbin[i]:
                if (y, x) not in lab.keys():
                    lab[(y, x)] = [(y+1, x)]
                else:
                    lab[(y, x)].append((y+1, x))
                if (y+1, x) not in lab.keys():
                    lab[(y+1, x)] = [(y, x)]
                else:
                    lab[(y+1, x)].append((y, x))
            else:
                if (y, x) not in lab.keys():
                    lab[(y, x)] = []
                if (y+1, x) not in lab.keys():
                    lab[(y+1, x)] = []
        hor_labs.append(reverse_lab(lab))
    
    labs = []
    for hor_lab in hor_labs:
        for ver_lab in ver_labs:
            lab = merge_labs(hor_lab, ver_lab)
            if lab not in labs:
                labs.append(lab)
    
    return labs


# --Generation brut-force--#

def generate_lab_bf(ncolumns, nlines):
    return [lab for lab in generate_pseudo_lab(ncolumns, nlines) if is_true_lab(lab)]


# --Generation Bilal--#

def genMerge(nlines, ncolumns):
    lab = {"nlines" : nlines, "ncolumns" : ncolumns}
    labtab = []                                          #contient les valeurs associées à chaque cellule du labyrinthe
    groups = {}                                          #contient les groupes de cellules de même valeur
    nwalls = nlines*(ncolumns - 1) + ncolumns*(nlines - 1)
        
    #initialisation de labtab et lab : les cellules ont initialement une valeur égale à leur rang
    #les groupes sont des singletons 
    for line in range(nlines):
        labtab += [[]]
        for col in range(ncolumns):
            labtab[line] += [nlines*line + col]
            lab[(line, col)] = []
            groups[nlines*line + col] = [(line, col)]
                
    #merge les valeurs tant que le toutes les cellules n'ont pas la même valeur
    while nlines*ncolumns - nlines - ncolumns != nwalls - 1:
        #on choisit une cellule aléatoire
        ncell = randint(0, nlines*ncolumns - 1) 
        cell = (ncell//ncolumns, ncell%ncolumns)
        vcell = labtab[cell[0]][cell[1]]
            
        #on choisit aléatoirement un voisin de cette cellule 
        adj = adjacent(cell, [nlines, ncolumns])
        chosen = adj[randint(0, len(adj)-1)]
        vchosen = labtab[chosen[0]][chosen[1]]
            
        #si les deux ont la même valeur on s'en fout
        if vcell==vchosen:
            continue
                
        #sinon on attribue la valeur de la première à toutes les cellules menant à la deuxième
        gchosen = groups[vchosen]
        for i in range(len(gchosen)):
            c = gchosen[i]
            labtab[c[0]][c[1]] = vcell
            groups[vcell] += [c]

        #puis on brise le mur entre les deux 
        lab[cell] += [chosen]
        lab[chosen] += [cell]
        nwalls -= 1

def genDumb(nlines, ncolumns):
    lab = {"nlines" : nlines, "ncolumns" : ncolumns}
    dejavu = []
    for i in range(nlines):
        dejavu += [[]]
        for j in range(ncolumns):
            dejavu[i] += [False]
            lab[(i, j)] = []
        
    #on choisit une cellule de départ
    nstartcell = randint(0, nlines*ncolumns - 1)
    startcell = (nstartcell//ncolumns, nstartcell%ncolumns)
        
    lastfree = [startcell] #on garde en mémoire les dernières cellules adjacentes à quelque part de nouveau
    position = startcell
        
    #on creuse jusqu'à n'en plus pouvoir
    onpeutcreuser = True
    while onpeutcreuser:
        dejavu += [position]
            
        #show_lab(lab)
            
        #on vérifie si la dernière case censée être adjacente à du nouveau l'est effectivement
        adjend = adjacent(lastfree[len(lastfree)-1], [nlines, ncolumns])
        #si elle ne l'est pas on la vire et on vérifie que celles d'avant le sont
        #si aucune ne l'est alors on a fini
        while [a for a in adjend if a not in dejavu]==[]:
            del lastfree[len(lastfree) - 1]
            if len(lastfree)==0:
                return lab
            adjend = adjacent(lastfree[len(lastfree)-1], [nlines, ncolumns])
                
        #on regarde les voisins de la cellule
        adj = adjacent(position, [nlines, ncolumns])
                
        #on regarde les cellules qu'on a pas déjà vues
        new = [a for a in adj if a not in dejavu]
        #si on est déjà passé autour on retourne là où on se rappelle avoir vu du neuf
        if new==[]:
            position = lastfree[len(lastfree)-1]
            continue
        #si elle a plus d'une cellule adjacente neuve, alors après avoir creusé il restera du neuf à côté
        if len(new)>1:
            lastfree += [position]
            chosen = new[randint(0, len(new)-1)]
                
        #si elle n'en a qu'une, pas trop le choix
        chosen = new[0]
            
        #on creuse
        lab[position] += [chosen]
        lab[chosen] += [position]
            
        #on se déplace
        position = chosen

def genExplore(nlines, ncolumns):
    
    def seuil(): #plus le seuil est grand, plus ça ressemble à dumb
        return randint(min(nlines-1,ncolumns-1), max(nlines-1, ncolumns-1))
    
    lab = {"nlines" : nlines, "ncolumns" : ncolumns}
    dejavu = []
    for i in range(nlines):
        dejavu += [[]]
        for j in range(ncolumns):
            dejavu[i] += [False]
            lab[(i, j)] = []
        
    #on choisit une cellule de départ
    nstartcell = randint(0, nlines*ncolumns - 1)
    startcell = (nstartcell//ncolumns, nstartcell%ncolumns)
        
    lastfree = [startcell] #on garde en mémoire les dernières cellules adjacentes à quelque part de nouveau
    position = startcell
    count = 0
        
    #on explore tout
    onpeutexplorer = True
    while onpeutexplorer:
        dejavu += [position]
            
        #show_lab(lab)
            
        #on actualise les cellules vues libres
        i = 0
        while i < len(lastfree):
            adj = adjacent(lastfree[i], [nlines, ncolumns])
            if [a for a in adj if a not in dejavu]==[]:
                del lastfree[i]
                continue
            i+=1
        if len(lastfree)==0:
            return lab
            
        #on regarde les voisins de la cellule
        adj = adjacent(position, [nlines, ncolumns])
                
        #on regarde les cellules qu'on a pas déjà vues
        new = [a for a in adj if a not in dejavu]
        #si on est déjà passé autour on retourne là où on se rappelle avoir vu du neuf
        if new==[]:
            position = lastfree[len(lastfree)-1]
            continue
        #si elle a plus d'une cellule adjacente neuve, alors après avoir creusé il restera du neuf à côté
        if len(new)>1:
            lastfree += [position]
            chosen = new[randint(0, len(new)-1)]
            
        #on crée aléatoirement un autre chemin sur une des cellules vues libres dispos si la branche est trop longue
        if count>seuil():
            position = lastfree[randint(0, len(lastfree)-1)]
            count = 0
            continue
                
        #si elle n'en a qu'une, pas trop le choix
        chosen = new[0]
            
        #on creuse
        lab[position] += [chosen]
        lab[chosen] += [position]
            
        #on se déplace
        position = chosen
        count += 1

def generateLab(nlines, ncolumns, method=genExplore):
    return method(nlines, ncolumns)


# --Generation Lucas--#

def generate_lab_deadends(ncolumns, nlines):
    lab = canonical_lab(ncolumns, nlines)
    res = [lab]
    return generate_lab_deadends_main(lab, res)

def generate_lab_deadends_main(lab, res, depth=0):
    sys.setrecursionlimit(10**6)
    print(depth, end=" | ")
    for deadend in get_deadends(lab):
        original_path = lab[deadend][0]
        for adj in adjacent(deadend, size=[lab["nlines"], lab["ncolumns"]]):
            current = deepcopy(lab)
            current[original_path].remove(deadend)
            if adj != original_path:
                current[deadend] = [adj]
                current[adj].append(deadend)
                if all(not lab_equality(current, result) for result in res):
                    res.append(current)
                    res = generate_lab_deadends_main(current, res, depth+1)
    return res
