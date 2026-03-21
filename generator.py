"""
Generateur procedural d'exercices style POFM Tour 1.
Chaque template genere des exercices uniques a chaque appel.
"""
import random
import math
from math import gcd


def lcm(a, b):
    return a * b // gcd(a, b)


# ============================================================
# CALCUL
# ============================================================

def calc_parentheses():
    """Style: oubli de parentheses"""
    a = random.randint(10, 30)
    b = random.randint(2, 9)
    c = random.randint(2, 9)
    correct = a - (b + c)
    wrong = a - b + c
    diff = wrong - correct
    names = [("Emma", "Noah"), ("Lea", "Hugo"), ("Chloe", "Lucas"), ("Jade", "Louis")]
    n1, n2 = random.choice(names)
    return {
        "theme": "calcul", "difficulty": 1,
        "statement": f"{n1} et {n2} doivent calculer {a} - ({b} + {c}). {n1} obtient la bonne reponse R. {n2} oublie les parentheses et calcule {a} - {b} + {c}, obtenant L. Que vaut L - R ?",
        "answer": diff,
        "explanation": f"R = {a} - ({b}+{c}) = {a} - {b+c} = {correct}. L = {a} - {b} + {c} = {wrong}. L - R = {wrong} - {correct} = {diff}."
    }


def calc_moyenne_manquante():
    """Style: trouver une note manquante"""
    n = random.randint(4, 6)
    notes = [random.randint(8, 19) for _ in range(n - 1)]
    moy = random.randint(12, 17)
    last = n * moy - sum(notes)
    if last < 0 or last > 20:
        return calc_moyenne_manquante()
    return {
        "theme": "calcul", "difficulty": 1,
        "statement": f"{n} eleves passent un controle note sur 20. Les notes des {n-1} premiers sont {', '.join(map(str, notes))}. La moyenne des {n} notes est {moy}. Quelle est la note du dernier eleve ?",
        "answer": last,
        "explanation": f"Somme des {n} notes = {n} x {moy} = {n*moy}. Somme des {n-1} premieres = {sum(notes)}. Derniere note = {n*moy} - {sum(notes)} = {last}."
    }


def calc_proportions():
    """Style: proportions en cascade"""
    objets = [
        ("jus d'orange", "sirop", "jus de citron"),
        ("farine", "sucre", "beurre"),
        ("eau", "lait", "creme"),
    ]
    o1, o2, o3 = random.choice(objets)
    k1 = random.randint(2, 5)
    k2 = random.randint(2, 4)
    base = random.randint(2, 6)
    mid = k2 * base
    top = k1 * mid
    return {
        "theme": "calcul", "difficulty": 1,
        "statement": f"Pour une recette, on utilise {k1} fois plus de {o1} que de {o2} et {k2} fois plus de {o2} que de {o3}. On a utilise {base} verres de {o3}. Combien de verres de {o1} a-t-on utilise ?",
        "answer": top,
        "explanation": f"{o3} = {base}. {o2} = {k2} x {base} = {mid}. {o1} = {k1} x {mid} = {top}."
    }


def calc_entiers_consecutifs():
    """Style: somme d'entiers consecutifs"""
    n = random.choice([3, 5, 7])
    mid = random.randint(100, 500)
    total = n * mid
    smallest = mid - n // 2
    largest = mid + n // 2
    return {
        "theme": "calcul", "difficulty": 2,
        "statement": f"La somme de {n} entiers consecutifs vaut {total}. Que vaut le plus grand de ces entiers ?",
        "answer": largest,
        "explanation": f"L'entier du milieu vaut {total}/{n} = {mid}. Le plus grand est {mid} + {n//2} = {largest}."
    }


def calc_equation_quadratique():
    """Style: x^2 - x = n, trouver x + k"""
    x = random.randint(5, 15)
    n = x * x - x
    k = random.randint(2, 8)
    names = ["Lea", "Remi", "Ines", "Tom"]
    name = random.choice(names)
    return {
        "theme": "calcul", "difficulty": 2,
        "statement": f"{name} choisit un nombre positif x, le met au carre et lui soustrait x. Il obtient {n}. Que vaut x + {k} ?",
        "answer": x + k,
        "explanation": f"x^2 - x = {n}, soit x^2 - x - {n} = 0. (x - {x})(x + {x-1}) = 0. Comme x > 0, x = {x}. Donc x + {k} = {x + k}."
    }


def calc_fraction_difference():
    """Style: (n+1)/n - n/(n+1) en fraction irreductible"""
    n = random.randint(100, 500)
    num = 2 * n + 1
    den = n * (n + 1)
    g = gcd(num, den)
    a = num // g
    return {
        "theme": "calcul", "difficulty": 3,
        "statement": f"La fraction {n+1}/{n} - {n}/{n+1} s'ecrit sous la forme d'une fraction irreductible a/b. Que vaut a ?",
        "answer": a,
        "explanation": f"{n+1}/{n} - {n}/{n+1} = ({(n+1)**2} - {n**2})/({n} x {n+1}) = {num}/{den}. PGCD({num},{den}) = {g}. Donc a = {a}."
    }


def calc_identite_remarquable():
    """Style: x+y et xy donnes, trouver x^2 + y^2 ou (x-y)^2"""
    x = random.randint(2, 12)
    y = random.randint(-8, 12)
    while y == x:
        y = random.randint(-8, 12)
    s = x + y
    p = x * y
    target = random.choice(["x2_plus_y2", "x_minus_y_squared"])
    if target == "x2_plus_y2":
        answer = s * s - 2 * p
        stmt = f"Les reels x et y verifient x + y = {s} et xy = {p}. Que vaut x^2 + y^2 ?"
        expl = f"x^2 + y^2 = (x+y)^2 - 2xy = {s}^2 - 2 x {p} = {s*s} - {2*p} = {answer}."
    else:
        answer = s * s - 4 * p
        stmt = f"Les reels x et y verifient x + y = {s} et xy = {p}. Que vaut (x - y)^2 ?"
        expl = f"(x-y)^2 = (x+y)^2 - 4xy = {s*s} - 4 x {p} = {s*s} - {4*p} = {answer}."
    return {
        "theme": "calcul", "difficulty": 3,
        "statement": stmt, "answer": answer, "explanation": expl
    }


def calc_somme_gauss():
    """Style: somme 1+2+...+n"""
    n = random.choice([50, 75, 80, 100, 120, 150, 200])
    answer = n * (n + 1) // 2
    return {
        "theme": "calcul", "difficulty": 2,
        "statement": f"Combien vaut la somme 1 + 2 + 3 + ... + {n} ?",
        "answer": answer,
        "explanation": f"Formule de Gauss : n(n+1)/2 = {n} x {n+1} / 2 = {answer}."
    }


def calc_somme_carres():
    """Style: somme des carres"""
    n = random.randint(8, 15)
    answer = n * (n + 1) * (2 * n + 1) // 6
    return {
        "theme": "calcul", "difficulty": 4,
        "statement": f"Que vaut la somme 1^2 + 2^2 + 3^2 + ... + {n}^2 ?",
        "answer": answer,
        "explanation": f"Formule : n(n+1)(2n+1)/6 = {n} x {n+1} x {2*n+1} / 6 = {answer}."
    }


def calc_produit_telescopique():
    """Style: produit (1+1/2)(1+1/3)...(1+1/n)"""
    n = random.randint(50, 500)
    # Product = (n+1)/2
    result_num = n + 1
    result_den = 2
    g = gcd(result_num, result_den)
    a, b = result_num // g, result_den // g
    return {
        "theme": "calcul", "difficulty": 4,
        "statement": f"Le nombre (1 + 1/2)(1 + 1/3)(1 + 1/4)...(1 + 1/{n}) s'ecrit sous la forme d'une fraction irreductible a/b. Que vaut a + b ?",
        "answer": a + b,
        "explanation": f"Chaque facteur (1+1/k) = (k+1)/k. Produit telescopique = {n+1}/2 = {a}/{b}. a + b = {a + b}."
    }


def calc_pourcentage():
    """Style: calcul de prix apres reduction"""
    prix = random.choice([40, 50, 60, 75, 80, 90, 100, 120, 150, 200])
    pct = random.choice([10, 15, 20, 25, 30, 40, 50])
    reduction = prix * pct // 100
    if reduction != prix * pct / 100:
        return calc_pourcentage()
    nouveau = prix - reduction
    return {
        "theme": "calcul", "difficulty": 1,
        "statement": f"Un article coute {prix} euros. Apres une reduction de {pct}%, quel est le nouveau prix en euros ?",
        "answer": nouveau,
        "explanation": f"Reduction = {pct}% de {prix} = {reduction} euros. Nouveau prix = {prix} - {reduction} = {nouveau} euros."
    }


def calc_partage():
    """Style: partage avec conditions"""
    b = random.randint(20, 80)
    k = random.randint(2, 4)
    a = k * b
    diff = random.randint(10, 40)
    c = a - diff
    if c <= 0:
        return calc_partage()
    total = a + b + c
    return {
        "theme": "calcul", "difficulty": 2,
        "statement": f"Trois amis se partagent une somme. Le premier recoit {k} fois ce que recoit le deuxieme. Le troisieme recoit {diff} euros de moins que le premier. Si le deuxieme recoit {b} euros, quelle est la somme totale ?",
        "answer": total,
        "explanation": f"Deuxieme = {b}. Premier = {k} x {b} = {a}. Troisieme = {a} - {diff} = {c}. Total = {a} + {b} + {c} = {total}."
    }


def calc_nombre_inverse():
    """Style: nombre a deux chiffres et son inverse"""
    u = random.randint(1, 4)
    d = random.randint(2, 4) * u
    if d > 9:
        return calc_nombre_inverse()
    nombre = 10 * d + u
    inverse = 10 * u + d
    diff = nombre - inverse
    return {
        "theme": "calcul", "difficulty": 3,
        "statement": f"Un nombre a deux chiffres est tel que le chiffre des dizaines vaut {d//u} fois le chiffre des unites. Si on inverse les chiffres, on obtient un nombre inferieur de {diff}. Quel est ce nombre ?",
        "answer": nombre,
        "explanation": f"Soit u le chiffre des unites, d = {d//u}u. Nombre = {10*(d//u)}u + u = {10*(d//u)+1}u. Inverse = 10u + {d//u}u = {10+d//u}u. Difference = {10*(d//u)+1 - 10 - d//u}u = {diff}, donc u = {u}. Nombre = {nombre}."
    }


# ============================================================
# GEOMETRIE
# ============================================================

def geo_cercle_rectangle():
    """Style: cercle circonscrit a un rectangle (triplets pythagoriciens)"""
    triplets = [(3,4,5),(5,12,13),(8,15,17),(7,24,25),(9,40,41),(6,8,10),(9,12,15),(12,16,20),(15,20,25)]
    a, b, c = random.choice(triplets)
    return {
        "theme": "geometrie", "difficulty": 1,
        "statement": f"On trace un rectangle de longueur {a} et de largeur {b}, puis on trace le cercle passant par les quatre sommets. Combien vaut le diametre du cercle ?",
        "answer": c,
        "explanation": f"La diagonale = diametre. Par Pythagore : sqrt({a}^2 + {b}^2) = sqrt({a*a + b*b}) = {c}."
    }


def geo_losange():
    """Style: aire d'un losange"""
    # On choisit des demi-diagonales qui forment un triplet pythagoricien
    triplets = [(3,4,5),(5,12,13),(8,15,17),(6,8,10),(9,12,15)]
    p, q, cote = random.choice(triplets)
    d1, d2 = 2 * p, 2 * q
    perim = 4 * cote
    aire = d1 * d2 // 2
    return {
        "theme": "geometrie", "difficulty": 2,
        "statement": f"Soit ABCD un losange de perimetre {perim}. La diagonale AC mesure {d1}. Que vaut l'aire du losange ?",
        "answer": aire,
        "explanation": f"Cote = {perim}/4 = {cote}. AO = {d1}/2 = {p}. OB = sqrt({cote}^2 - {p}^2) = {q}. BD = {d2}. Aire = ({d1} x {d2})/2 = {aire}."
    }


def geo_triangle_isocele():
    """Style: angles d'un triangle isocele"""
    apex = random.choice([20, 30, 36, 40, 50, 60, 70, 80, 100, 120])
    base_angle = (180 - apex) // 2
    if base_angle * 2 + apex != 180:
        return geo_triangle_isocele()
    return {
        "theme": "geometrie", "difficulty": 1,
        "statement": f"Soit ABC un triangle isocele en A tel que l'angle BAC = {apex} degres. Que vaut l'angle ABC (en degres) ?",
        "answer": base_angle,
        "explanation": f"Isocele en A : angles a la base egaux. {apex} + 2 x angle ABC = 180. Angle ABC = (180 - {apex})/2 = {base_angle}."
    }


def geo_triangle_isocele_sur_cote():
    """Style: angle ADB avec D sur AC et DC=DB"""
    angle_c = random.randint(20, 85)
    angle_bdc = 180 - 2 * angle_c
    angle_adb = 180 - angle_bdc
    return {
        "theme": "geometrie", "difficulty": 2,
        "statement": f"Soit ABC un triangle avec l'angle BCA = {angle_c} degres. D est un point de [AC] tel que DC = DB. Quelle est la mesure (en degres) de l'angle ADB ?",
        "answer": angle_adb,
        "explanation": f"Triangle BDC isocele en D : angle DBC = angle DCB = {angle_c}. Angle BDC = 180 - 2 x {angle_c} = {angle_bdc}. Angle ADB = 180 - {angle_bdc} = {angle_adb}."
    }


def geo_perimetre_pythagoricien():
    """Style: perimetre d'un triangle rectangle"""
    triplets = [(3,4,5),(5,12,13),(8,15,17),(7,24,25),(9,40,41),(20,21,29)]
    a, b, c = random.choice(triplets)
    k = random.randint(1, 3)
    a, b, c = a * k, b * k, c * k
    return {
        "theme": "geometrie", "difficulty": 2,
        "statement": f"Un triangle rectangle a pour cotes de l'angle droit {a} et {b}. Que vaut son perimetre ?",
        "answer": a + b + c,
        "explanation": f"Hypotenuse = sqrt({a}^2 + {b}^2) = sqrt({a*a+b*b}) = {c}. Perimetre = {a} + {b} + {c} = {a+b+c}."
    }


def geo_rectangle_aire():
    """Style: rectangle avec perimetre et relation L/l"""
    diff = random.randint(2, 10)
    l = random.randint(3, 15)
    L = l + diff
    perim = 2 * (L + l)
    aire = L * l
    return {
        "theme": "geometrie", "difficulty": 2,
        "statement": f"Un rectangle a un perimetre de {perim} cm et sa longueur fait {diff} cm de plus que sa largeur. Que vaut l'aire du rectangle (en cm^2) ?",
        "answer": aire,
        "explanation": f"Soit x la largeur. 2(x + x + {diff}) = {perim}, 4x + {2*diff} = {perim}, x = {l}. Longueur = {L}. Aire = {L} x {l} = {aire}."
    }


def geo_carrelage():
    """Style: combien de carreaux pour couvrir une piece"""
    carreau = random.choice([20, 25, 30, 40, 50, 60, 80])
    nx = random.randint(8, 25)
    ny = random.randint(6, 20)
    longueur_cm = nx * carreau
    largeur_cm = ny * carreau
    longueur_m = longueur_cm / 100
    largeur_m = largeur_cm / 100
    total = nx * ny
    return {
        "theme": "geometrie", "difficulty": 1,
        "statement": f"Pour carreler une piece de {longueur_m}m de long et {largeur_m}m de large, on dispose de carreaux carres de {carreau}cm de cote. Combien de carreaux faut-il ?",
        "answer": total,
        "explanation": f"En longueur : {longueur_cm}/{carreau} = {nx}. En largeur : {largeur_cm}/{carreau} = {ny}. Total = {nx} x {ny} = {total}."
    }


def geo_diagonales_rectangle():
    """Style: aire des triangles formes par les diagonales"""
    a = random.randint(4, 15)
    b = random.randint(4, 15)
    while a == b:
        b = random.randint(4, 15)
    aire_rect = a * b
    aire_triangle = aire_rect // 4
    if aire_rect % 4 != 0:
        return geo_diagonales_rectangle()
    return {
        "theme": "geometrie", "difficulty": 3,
        "statement": f"Un rectangle ABCD a pour dimensions {a} et {b}. Les diagonales se coupent en O. Que vaut l'aire du triangle AOB ?",
        "answer": aire_triangle,
        "explanation": f"Les diagonales se coupent en leur milieu et forment 4 triangles egaux. Aire = {aire_rect}/4 = {aire_triangle}."
    }


def geo_aire_triangle_coordonnees():
    """Style: aire d'un triangle avec coordonnees"""
    x1, y1 = 0, 0
    x2 = random.randint(4, 12)
    y2 = 0
    x3 = random.randint(1, x2 - 1)
    y3 = random.randint(2, 10)
    base = x2
    hauteur = y3
    aire = base * hauteur // 2
    if base * hauteur % 2 != 0:
        return geo_aire_triangle_coordonnees()
    return {
        "theme": "geometrie", "difficulty": 3,
        "statement": f"Dans un repere, les points A({x1},{y1}), B({x2},{y2}) et C({x3},{y3}) forment un triangle. Que vaut son aire ?",
        "answer": aire,
        "explanation": f"Base AB = {x2} (horizontale). Hauteur = ordonnee de C = {y3}. Aire = {x2} x {y3} / 2 = {aire}."
    }


def geo_trapeze():
    """Style: aire d'un trapeze"""
    b1 = random.randint(5, 20)
    b2 = random.randint(3, b1 - 1)
    h = random.randint(3, 12)
    total = (b1 + b2) * h
    if total % 2 != 0:
        h = random.choice([h + 1 if h % 2 == 1 else h, h])
        total = (b1 + b2) * h
        if total % 2 != 0:
            return geo_trapeze()
    aire = total // 2
    return {
        "theme": "geometrie", "difficulty": 3,
        "statement": f"Soit ABCD un trapeze rectangle en A et D, avec AB = {b1}, CD = {b2} et AD = {h}. Que vaut l'aire du trapeze ?",
        "answer": aire,
        "explanation": f"Aire = (AB + CD) x AD / 2 = ({b1} + {b2}) x {h} / 2 = {(b1+b2)} x {h} / 2 = {aire}."
    }


def geo_cube_visible():
    """Style: cubes visibles dans un grand cube"""
    n = random.choice([5, 6, 7, 8, 9, 10, 12])
    total = n ** 3
    invisible = (n - 2) ** 2 * (n - 1)
    visible = total - invisible
    return {
        "theme": "geometrie", "difficulty": 4,
        "statement": f"Un grand cube forme de {total} petits cubes ({n}x{n}x{n}) est pose sur une table. Combien de petits cubes ont au moins une face visible ? (Le dessous n'est pas visible)",
        "answer": visible,
        "explanation": f"Invisible = pas sur le dessus ni les 4 cotes. {n-2} x {n-2} x {n-1} = {invisible}. Visible = {total} - {invisible} = {visible}."
    }


# ============================================================
# ARITHMETIQUE
# ============================================================

def arith_carres_parfaits():
    """Style: combien de carres parfaits <= N"""
    n = random.choice([200, 300, 400, 500, 600, 700, 800, 900, 1000, 1500, 2000])
    answer = int(math.isqrt(n))
    return {
        "theme": "arithmetique", "difficulty": 1,
        "statement": f"Combien y a-t-il de carres parfaits compris entre 1 et {n} (inclus) ?",
        "answer": answer,
        "explanation": f"On cherche n tel que n^2 <= {n}. {answer}^2 = {answer**2} <= {n} et {answer+1}^2 = {(answer+1)**2} > {n}. Il y en a {answer}."
    }


def arith_ppcm():
    """Style: PPCM de 1 a n"""
    n = random.choice([6, 7, 8, 9, 10, 12])
    result = 1
    for i in range(1, n + 1):
        result = lcm(result, i)
    return {
        "theme": "arithmetique", "difficulty": 2,
        "statement": f"Quel est le plus petit entier strictement positif qui soit multiple de tous les entiers de 1 a {n} (inclus) ?",
        "answer": result,
        "explanation": f"On calcule le PPCM(1, 2, ..., {n}) = {result}."
    }


def arith_pgcd():
    """Style: PGCD de deux nombres"""
    g = random.randint(6, 50)
    a_mult = random.randint(2, 8)
    b_mult = random.randint(2, 8)
    while gcd(a_mult, b_mult) != 1:
        b_mult = random.randint(2, 8)
    a = g * a_mult
    b = g * b_mult
    return {
        "theme": "arithmetique", "difficulty": 2,
        "statement": f"Quel est le PGCD de {a} et {b} ?",
        "answer": g,
        "explanation": f"{a} = {g} x {a_mult}, {b} = {g} x {b_mult}. Comme PGCD({a_mult},{b_mult}) = 1, PGCD({a},{b}) = {g}."
    }


def arith_inclusion_exclusion():
    """Style: divisibles par a ou b dans [1,N]"""
    N = random.choice([80, 100, 120, 150, 200, 300, 500])
    primes = [2, 3, 5, 7, 11, 13]
    a = random.choice(primes)
    b = random.choice([p for p in primes if p != a])
    if a > b:
        a, b = b, a
    c = a * b  # lcm since both prime
    da = N // a
    db = N // b
    dc = N // c
    answer = da + db - dc
    return {
        "theme": "arithmetique", "difficulty": 2,
        "statement": f"Combien d'entiers compris entre 1 et {N} (inclus) sont divisibles par {a} ou par {b} ?",
        "answer": answer,
        "explanation": f"Multiples de {a} : {da}. Multiples de {b} : {db}. Multiples de {c} : {dc}. Par inclusion-exclusion : {da} + {db} - {dc} = {answer}."
    }


def arith_chiffre_dans_liste():
    """Style: combien de fois un chiffre apparait"""
    N = random.choice([100, 200, 500])
    d = random.randint(1, 9)
    count = 0
    for i in range(1, N + 1):
        count += str(i).count(str(d))
    return {
        "theme": "arithmetique", "difficulty": 3,
        "statement": f"On ecrit tous les entiers de 1 a {N}. Combien de fois le chiffre {d} apparait-il au total ?",
        "answer": count,
        "explanation": f"En comptant le chiffre {d} dans chaque position (unites, dizaines, centaines...) de 1 a {N}, on trouve {count} apparitions."
    }


def arith_nombre_diviseurs():
    """Style: nombre de diviseurs de n"""
    # n = p^a * q^b
    p, q = 2, 3
    a = random.randint(2, 8)
    b = random.randint(1, 5)
    n_repr = f"2^{a} x 3^{b}" if b > 1 else f"2^{a} x 3"
    answer = (a + 1) * (b + 1)
    return {
        "theme": "arithmetique", "difficulty": 3,
        "statement": f"Combien de diviseurs positifs possede le nombre {n_repr} ?",
        "answer": answer,
        "explanation": f"Pour n = p^a x q^b, le nombre de diviseurs = (a+1)(b+1) = ({a}+1)({b}+1) = {answer}."
    }


def arith_zeros_factorielle():
    """Style: zeros a la fin de n!"""
    n = random.choice([20, 25, 30, 40, 50, 75, 100, 125, 150, 200])
    count = 0
    power = 5
    while power <= n:
        count += n // power
        power *= 5
    return {
        "theme": "arithmetique", "difficulty": 4,
        "statement": f"Combien de zeros y a-t-il a la fin de {n}! (factorielle de {n}) ?",
        "answer": count,
        "explanation": f"On compte la puissance de 5 dans {n}! : " + " + ".join([f"floor({n}/{5**i})" for i in range(1, 10) if 5**i <= n]) + f" = {count}."
    }


def arith_puissances():
    """Style: 9^n / 3 = 3^a"""
    exp = random.randint(50, 300)
    answer = 2 * exp - 1
    return {
        "theme": "arithmetique", "difficulty": 4,
        "statement": f"Soit n = 9^{exp}. Le nombre n/3 peut s'ecrire sous la forme 3^a. Que vaut a ?",
        "answer": answer,
        "explanation": f"9^{exp} = (3^2)^{exp} = 3^{2*exp}. n/3 = 3^{2*exp}/3 = 3^{answer}. Donc a = {answer}."
    }


def arith_factorielle_divisible():
    """Style: plus petit n tel que n! divisible par k"""
    # k = 2^a * 5^b, we need enough 5s
    b = random.randint(2, 5)
    k = 10 ** b
    n = 5
    while True:
        count = 0
        power = 5
        while power <= n:
            count += n // power
            power *= 5
        if count >= b:
            break
        n += 1
    return {
        "theme": "arithmetique", "difficulty": 5,
        "statement": f"Quel est le plus petit entier positif n tel que n! soit divisible par {k} ?",
        "answer": n,
        "explanation": f"{k} = 10^{b} = 2^{b} x 5^{b}. Il faut {b} facteurs 5 dans n!. Pour n = {n}, la puissance de 5 dans {n}! est >= {b}. Donc n = {n}."
    }


def arith_non_divisibles():
    """Style: entiers non divisibles par 2, 3 ou 5"""
    N = random.choice([100, 200, 300, 500, 1000])
    d2 = N // 2
    d3 = N // 3
    d5 = N // 5
    d6 = N // 6
    d10 = N // 10
    d15 = N // 15
    d30 = N // 30
    divisibles = d2 + d3 + d5 - d6 - d10 - d15 + d30
    answer = N - divisibles
    return {
        "theme": "arithmetique", "difficulty": 5,
        "statement": f"Combien d'entiers entre 1 et {N} ne sont divisibles ni par 2, ni par 3, ni par 5 ?",
        "answer": answer,
        "explanation": f"Par inclusion-exclusion, {divisibles} sont divisibles par 2, 3 ou 5. Non divisibles : {N} - {divisibles} = {answer}."
    }


def arith_chiffres_croissants():
    """Style: nombres a 3 chiffres croissants"""
    # C(9,3) = 84 toujours, mais on peut varier la borne
    lo = random.choice([100, 200, 300])
    hi = random.choice([700, 800, 999])
    count = 0
    for n in range(max(lo, 123), hi + 1):
        s = str(n)
        if len(s) == 3 and s[0] < s[1] < s[2] and s[0] != '0':
            count += 1
    return {
        "theme": "arithmetique", "difficulty": 3,
        "statement": f"Combien d'entiers compris entre {lo} et {hi} ont 3 chiffres distincts formant une suite strictement croissante ?",
        "answer": count,
        "explanation": f"On cherche les nombres a 3 chiffres dans [{lo},{hi}] dont les chiffres sont strictement croissants. Il y en a {count}."
    }


# ============================================================
# COMBINATOIRE
# ============================================================

def combi_chaussettes():
    """Style: principe des tiroirs"""
    couleurs = random.randint(3, 5)
    noms = ["noires", "blanches", "rouges", "bleues", "vertes"][:couleurs]
    quantites = [random.randint(30, 80) for _ in range(couleurs)]
    max_q = max(quantites)
    answer = max_q + 1
    desc = ", ".join([f"{q} {n}" for q, n in zip(quantites, noms)])
    return {
        "theme": "combinatoire", "difficulty": 1,
        "statement": f"Un tiroir contient {desc}. Combien de chaussettes faut-il prendre au minimum pour etre sur d'avoir deux chaussettes de couleurs differentes ?",
        "answer": answer,
        "explanation": f"Pire cas : on prend toutes les chaussettes d'une couleur ({max_q}), puis une de plus. Reponse = {max_q} + 1 = {answer}."
    }


def combi_droites_regions():
    """Style: minimum de regions avec n droites"""
    n = random.randint(5, 50)
    answer = n + 1
    return {
        "theme": "combinatoire", "difficulty": 1,
        "statement": f"On trace {n} droites distinctes dans un plan. Combien de regions delimitent-elles au minimum ?",
        "answer": answer,
        "explanation": f"Le minimum est atteint quand toutes les droites sont paralleles : n + 1 = {answer} regions."
    }


def combi_barres_etoiles():
    """Style: repartition de bonbons/parts"""
    personnes = random.randint(3, 5)
    total = random.randint(8, 15)
    noms = ["Alice, Baptiste et Clara",
            "Anna, Basile, Camille et Damien",
            "Agathe, Bruno, Celia, David et Eva"]
    nom = noms[personnes - 3] if personnes - 3 < len(noms) else f"{personnes} personnes"
    reste = total - personnes
    answer = math.comb(reste + personnes - 1, personnes - 1)
    return {
        "theme": "combinatoire", "difficulty": 3,
        "statement": f"{nom} veulent se partager {total} bonbons identiques de sorte que chacun en ait au moins un. Combien de repartitions sont possibles ?",
        "answer": answer,
        "explanation": f"On donne 1 bonbon a chacun, reste {reste} a repartir entre {personnes} personnes. C({reste}+{personnes-1},{personnes-1}) = C({reste+personnes-1},{personnes-1}) = {answer}."
    }


def combi_combinaisons():
    """Style: choisir k parmi n"""
    n = random.randint(6, 12)
    k = random.randint(2, min(4, n))
    answer = math.comb(n, k)
    contextes = [
        f"De combien de facons peut-on choisir {k} delegues parmi {n} eleves ?",
        f"Combien de groupes de {k} personnes peut-on former a partir de {n} personnes ?",
        f"Un examen propose {n} exercices. Combien de facons y a-t-il d'en choisir {k} ?",
    ]
    return {
        "theme": "combinatoire", "difficulty": 2,
        "statement": random.choice(contextes),
        "answer": answer,
        "explanation": f"C({n},{k}) = {n}! / ({k}! x {n-k}!) = {answer}."
    }


def combi_arrangements():
    """Style: nombres avec chiffres sans repetition"""
    digits = random.randint(4, 7)
    places = random.randint(2, 3)
    answer = 1
    for i in range(places):
        answer *= (digits - i)
    return {
        "theme": "combinatoire", "difficulty": 2,
        "statement": f"Combien de nombres de {places} chiffres peut-on former avec les chiffres 1 a {digits} sans repetition ?",
        "answer": answer,
        "explanation": f"{'x'.join([str(digits - i) for i in range(places)])} = {answer}."
    }


def combi_fibonacci_escalier():
    """Style: monter un escalier 1 ou 2 marches"""
    n = random.randint(6, 12)
    fib = [0] * (n + 1)
    fib[1] = 1
    fib[2] = 2
    for i in range(3, n + 1):
        fib[i] = fib[i-1] + fib[i-2]
    return {
        "theme": "combinatoire", "difficulty": 3,
        "statement": f"De combien de manieres peut-on monter un escalier de {n} marches si on peut monter 1 ou 2 marches a la fois ?",
        "answer": fib[n],
        "explanation": f"Suite de Fibonacci : f(1)=1, f(2)=2, f(n)=f(n-1)+f(n-2). f({n}) = {fib[n]}."
    }


def combi_des():
    """Style: somme de 3 des"""
    target = random.randint(8, 13)
    count = 0
    for a in range(1, 7):
        for b in range(1, 7):
            for c in range(1, 7):
                if a + b + c == target:
                    count += 1
    return {
        "theme": "combinatoire", "difficulty": 4,
        "statement": f"On lance trois des classiques. Combien de resultats donnent une somme egale a {target} ?",
        "answer": count,
        "explanation": f"On compte les triplets (a,b,c) avec 1 <= a,b,c <= 6 et a+b+c = {target}. Il y en a {count}."
    }


def combi_pieces():
    """Style: decomposition en pieces"""
    montant = random.choice([8, 10, 12, 15, 20])
    count = 0
    for c5 in range(montant // 5 + 1):
        for c2 in range((montant - 5 * c5) // 2 + 1):
            c1 = montant - 5 * c5 - 2 * c2
            if c1 >= 0:
                count += 1
    return {
        "theme": "combinatoire", "difficulty": 4,
        "statement": f"On dispose de pieces de 1, 2 et 5 euros. De combien de facons peut-on faire {montant} euros ?",
        "answer": count,
        "explanation": f"On enumere systematiquement les decompositions de {montant} en pieces de 1, 2 et 5. Il y en a {count}."
    }


def combi_nombres_somme_chiffres():
    """Style: nombres a 4 chiffres avec somme de chiffres = s"""
    s = random.randint(4, 7)
    count = 0
    for n in range(1000, 10000):
        if sum(int(d) for d in str(n)) == s:
            count += 1
    return {
        "theme": "combinatoire", "difficulty": 4,
        "statement": f"Combien de nombres a 4 chiffres (de 1000 a 9999) ont une somme de chiffres egale a {s} ?",
        "answer": count,
        "explanation": f"On cherche (a,b,c,d) avec a >= 1, b,c,d >= 0 et a+b+c+d = {s}. On pose a' = a-1, et on applique barres et etoiles. Il y en a {count}."
    }


def combi_train_wagons():
    """Style: wagons periodiques"""
    period = 3
    # Number of wagons must be such that it's not divisible by 3
    n_wagons = random.choice([10, 11, 13, 14, 16, 17, 19])
    sum_per_3 = random.randint(30, 60)

    # Count wagons of each type
    count1 = (n_wagons + 2) // 3  # type w1 (positions 1,4,7,...)
    count2 = (n_wagons + 1) // 3  # type w2
    count3 = n_wagons // 3        # type w3

    # w1 + w2 + w3 = sum_per_3
    # count1*w1 + count2*w2 + count3*w3 = total
    # We want w1 to be a nice integer
    w1 = random.randint(5, 20)
    total = count1 * w1 + (sum_per_3 - w1) * min(count2, count3)
    # Recalculate properly
    # total = count1*w1 + count2*w2 + count3*w3 with w2+w3 = sum_per_3 - w1
    # Let's just pick total so that w1 = (total - min(count2,count3) * sum_per_3) / (count1 - min(count2,count3))
    # Simpler: force it
    w2 = random.randint(5, sum_per_3 - w1 - 2)
    w3 = sum_per_3 - w1 - w2
    if w3 <= 0:
        return combi_train_wagons()
    total = count1 * w1 + count2 * w2 + count3 * w3

    # Which wagon do we ask about?
    ask = random.choice([4, 7, 10])
    while ask > n_wagons:
        ask = random.choice([4, 7])
    # wagon ask is type w1 if (ask-1) % 3 == 0
    idx = (ask - 1) % 3
    answer = [w1, w2, w3][idx]

    return {
        "theme": "combinatoire", "difficulty": 3,
        "statement": f"Un train de {n_wagons} wagons transporte {total} passagers. Si on choisit 3 wagons consecutifs, on compte toujours {sum_per_3} passagers. Combien y a-t-il de passagers dans le wagon {ask} ?",
        "answer": answer,
        "explanation": f"La suite est periodique de periode 3. w1={w1}, w2={w2}, w3={w3}. Le wagon {ask} est de type w{idx+1} = {answer}."
    }


# ============================================================
# REGISTRE DE TOUS LES GENERATEURS
# ============================================================

GENERATORS = {
    "calcul": [
        (1, calc_parentheses),
        (1, calc_moyenne_manquante),
        (1, calc_proportions),
        (1, calc_pourcentage),
        (2, calc_entiers_consecutifs),
        (2, calc_equation_quadratique),
        (2, calc_somme_gauss),
        (2, calc_partage),
        (3, calc_fraction_difference),
        (3, calc_identite_remarquable),
        (3, calc_nombre_inverse),
        (4, calc_somme_carres),
        (4, calc_produit_telescopique),
    ],
    "geometrie": [
        (1, geo_cercle_rectangle),
        (1, geo_triangle_isocele),
        (1, geo_carrelage),
        (2, geo_losange),
        (2, geo_triangle_isocele_sur_cote),
        (2, geo_perimetre_pythagoricien),
        (2, geo_rectangle_aire),
        (3, geo_diagonales_rectangle),
        (3, geo_aire_triangle_coordonnees),
        (3, geo_trapeze),
        (4, geo_cube_visible),
    ],
    "arithmetique": [
        (1, arith_carres_parfaits),
        (2, arith_ppcm),
        (2, arith_pgcd),
        (2, arith_inclusion_exclusion),
        (3, arith_chiffre_dans_liste),
        (3, arith_nombre_diviseurs),
        (3, arith_chiffres_croissants),
        (4, arith_zeros_factorielle),
        (4, arith_puissances),
        (5, arith_factorielle_divisible),
        (5, arith_non_divisibles),
    ],
    "combinatoire": [
        (1, combi_chaussettes),
        (1, combi_droites_regions),
        (2, combi_combinaisons),
        (2, combi_arrangements),
        (3, combi_barres_etoiles),
        (3, combi_fibonacci_escalier),
        (3, combi_train_wagons),
        (4, combi_des),
        (4, combi_pieces),
        (4, combi_nombres_somme_chiffres),
    ],
}


def generate_exercise(theme=None, difficulty=None):
    """Genere un exercice aleatoire."""
    candidates = []
    for t, gens in GENERATORS.items():
        if theme and theme != "all" and t != theme:
            continue
        for diff, gen in gens:
            if difficulty and difficulty > 0 and diff != difficulty:
                continue
            candidates.append(gen)

    if not candidates:
        return None

    gen = random.choice(candidates)
    ex = gen()
    ex["id"] = random.randint(10000, 99999)  # ID unique genere
    ex["generated"] = True
    return ex


def generate_exam(n=25):
    """Genere un concours blanc de n exercices."""
    targets = {1: 5, 2: 6, 3: 6, 4: 5, 5: 3}
    exercises = []
    for diff, count in targets.items():
        for _ in range(count):
            ex = generate_exercise(difficulty=diff)
            if ex:
                exercises.append(ex)
    # Completer si necessaire
    while len(exercises) < n:
        ex = generate_exercise()
        if ex:
            exercises.append(ex)
    exercises = exercises[:n]
    exercises.sort(key=lambda e: e["difficulty"])
    for i, ex in enumerate(exercises, 1):
        ex["num"] = i
    return exercises
