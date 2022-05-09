import numpy as np
import random
from copy import deepcopy
import sys


# Encoding
def encodeLab(tab):
    """
    Transform a nested list of the form
    [
        ["g", "db"],
        ["g", "dh"]
    ]
    
    Into a dict of the form
    {
     nlines:   2,
     ncolumns: 2,
     (0,0): [(0,1)], (0,1): [(0,0), (1,1)],
     (1,0): [(1,1)], (1,1): [(1,0), (0,1)]
    }
    """
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

# Decoding
def decodeLab(lab):
    """
    Transform a dict of the form
    {
     nlines:   2,
     ncolumns: 2,
     (0,0): [(0,1)], (0,1): [(0,0), (1,1)],
     (1,0): [(1,1)], (1,1): [(1,0), (0,1)]
    }
    
    Into a nested list of the form
    [
        ["g", "db"],
        ["g", "dh"]
    ]
    
    """
    tab = [["" for j in range(lab["ncolumns"])] for i in range(lab["nlines"])]
    for i in range(len(tab)):
        for j in range(len(tab[i])):
            if (i-1, j) in lab[(i, j)]:
                tab[i][j] += 'h'
            if (i, j+1) in lab[(i, j)]:
                tab[i][j] += 'd'
            if (i+1, j) in lab[(i, j)]:
                tab[i][j] += 'b'
            if (i, j-1) in lab[(i, j)]:
                tab[i][j] += 'g'
    return tab

def nb_murs(lab):
    """
    Get the number of walls in a given lab
    """
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

def adjacent(cell, size=None):
    """
    Return the cooridinates of the cells adjacent to a given cell
    size: [nlines, ncolumns] to avoid returning out-of-bound coordinates
    """
    if size==None:
        return [
            (cell[0]-1, cell[1]  ),
            (cell[0]  , cell[1]-1),
            (cell[0]+1, cell[1]  ),
            (cell[0]  , cell[1]+1)
        ]
    return [adj for adj in adjacent(cell) if (adj[0]>=0 and adj[0]<size[0] and adj[1]>=0 and adj[1]<size[1])]

def get_cell_occurence(lab, cell=(0, 0), previous=None, markList=None):
    """
    Return 2d matrix of integers where the cell (y, x) contain the number of paths through which the cell (y, x) of a the given lab is accessible from the cell (0, 0)
    A labyrinth is valid iff the matrix only contains "1"'s
    """
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
    """
    Takes two labs merge them, returning a lab containing all the walls from lab1 and lab2
    """
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
    """
    Replace each connection by a wall and each wall by a connection in a given lab
    """
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
    """
    Return a lab of size n*m with no connection between any cell
    """
    lab = {"nlines":m, "ncolumns":n}
    for x in range(n):
        for y in range(m):
            lab[(y, x)] = []
    return lab

def canonical_lab(n, m):
    """
    Return an obvious lab of size n*m
        (Canonical)
    """
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
    """
    Return a list of all the dead-ends in a given lab
    """
    deadends = []
    for cell in lab.keys():
        if type(cell) != type("a"):
            if len(lab[cell]) == 1 and cell != (0, 0):
                deadends.append(cell)
    return deadends

def lab_equality(lab1, lab2):
    """
    Check if two labs are identical
    """
    if lab1["ncolumns"] != lab1["ncolumns"] or lab1["nlines"] != lab2["nlines"]:
        return False
    return all(set(lab1[cell]) == set(lab2[cell]) for cell in lab1.keys() if type(cell) != type("a"))

def is_well_defined(lab):
    """
    Check if a lab is well defined:
    - All cells of the lab exist
    - All cells are inbound
    - No cell is connected to a non-adjacent cell
    """
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
    """
    Check if a lab is valid
    - It is connex
    - It doesn't contain loops
    """
    for line in get_cell_occurence(lab):
        for cell in line:
            if cell !=1:
                return False
    return True

# --Enumération--

def laplace(n, m):
    """
    Return the Laplacian Matrix assciated to the lab
    (see https://fr.wikipedia.org/wiki/Th%C3%A9or%C3%A8me_de_Kirchhoff)
    """
    full_grid = reverse_lab(empty_lab(n, m))
    inline_grid = [full_grid[(y,x)] for y in range(m) for x in range(n)]
    l = np.zeros((n*m, n*m)).astype("int64")
    for i in range(len(inline_grid)):
        for k in range(l.shape[1]):
            if i == k:
                l[i, k] = len(inline_grid[i])
            elif i in [y*n+x for y, x in inline_grid[k]]:
                l[i, k] = -1
            else:
                l[i, k] = 0
    return l

def kirchhoff(n, m):
    """
    Return the number of labs of size n*m
    """
    l = laplace(n,m)[:-1, :-1]
    return round(np.linalg.det(l))


# ---Generation pseudo-lab---#

def get_bin_list(n, nmax):
    """
    return a list of digits of the binary representation of n
    nmax is the maximum theoretical value of n, used to add 0 at the front of the list if necessary
    """
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
    """
    Generate the list of pseudo-labs of size n*m
    """
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
    """
    generate the list of all n*m labs by checking for each pseudo-lab if it is a true pseud-lab
    """
    return [lab for lab in generate_pseudo_lab(ncolumns, nlines) if is_true_lab(lab)]


# --Generation Bilal--#



# --Generation Random-- #

def unvisited_cells(marks):
    m = len(marks)
    n = len(marks[0])
    l = []
    for y in range(m):
        for x in range(n):
            if not marks[y][x]:
                l.append((y, x))
    return l

def add_path(lab, path, marks):
    cell = path.pop()
    while len(path):
        marks[cell[0]][cell[1]] = True
        next_cell = path.pop()
        lab[cell].append(next_cell)
        lab[next_cell] = [cell]
        cell = next_cell
    marks[cell[0]][cell[1]] = True
    return lab

def loop_erased_path(start, marks):
    shape = (len(marks), len(marks[0]))
    path = [start]
    
    while True:
        neighbourghs = adjacent(path[-1], shape)
        cell = neighbourghs[random.randint(0, len(neighbourghs)-1)]
        
        if cell in path:
            while path.pop() != cell:
                pass
        path.append(cell)
        
        if marks[cell[0]][cell[1]]:
            return path
    
def wilson_routine(lab, marks):
    while not all(all(mark) for mark in marks):
        unvisited = unvisited_cells(marks)
        start = unvisited[random.randint(0, len(unvisited)-1)]
        path = loop_erased_path(start, marks)
        add_path(lab, path, marks)
    return lab

def wilson_generation(n, m):
    lab = {"nlines": m, "ncolumns": n}
    marks = [[False for _ in range(n)] for _ in range(m)]
    y = random.randint(0, m-1)
    x = random.randint(0, n-1)
    marks[y][x] = True
    lab[(y, x)] = []
    return wilson_routine(lab, marks)


# --Generation Lucas-- #

def generate_lab_deadends_routine(lab, res):
    stack = [lab]
    while len(stack)>0:
        lab = stack.pop()
        for deadend in get_deadends(lab):
            original_path = lab[deadend][0]
            for adj in adjacent(deadend, size=[lab["nlines"], lab["ncolumns"]]):
                current = deepcopy(lab)
                current[original_path].remove(deadend)
                if adj != original_path:
                    current[deadend] = [adj]
                    current[adj].append(deadend)
                    prev_len = len(res)
                    if all(not lab_equality(current, other) for other in res):
                        res.append(current)
                        stack.append(current)
    return res

def generate_lab_deadends(ncolumns, nlines):
    """
    Recursively generate the list of all n*m labs
    """
    lab = canonical_lab(ncolumns, nlines)
    res = [lab]
    return generate_lab_deadends_routine(lab, res)

# generation bilal

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



if __name__ == '__main__':
    print(len(generate_lab_deadends(3,4)))