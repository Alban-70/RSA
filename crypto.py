from math import gcd
from random import choice, randint

###### Exercice 1 #######

def inverseModulaire(e, m):
    if gcd(e, m) != 1:
        return 0

    d = 1
    while d <= m - 1:
        if (e * d) % m == 1:
            return d
        d += 1

    return -1

def estPremier(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True

def premierAleatoire(inf, lg):
    tentatives_max = lg * 20 
    for i in range(tentatives_max):
        candidat = randint(inf, inf + lg)
        if estPremier(candidat):
            return candidat
    
    return -1

def premierAleatoireAvecRandom(n):
    if n <= 2:
        return -1
    
    tentatives_max = (n - 2) * 10
    
    for i in range(tentatives_max):
        candidat = randint(2, n - 1)
        if gcd(candidat, n) == 1:
            return candidat
    
    return -1

def premierAleatoireAvec(n, a):
    if n <= 2:
        return False
    if gcd(a, n) == 1:
        return True
    
    return False

def expoModulaire(x, e, n):
    if e == 0:
        return 1
    
    f = expoModulaire(x, e // 2, n)
    
    if e % 2 == 0:
        return (f * f) % n
    else:
        return (x * f * f) % n
    

###### Exercice 2 #######

def choixCle(inf, lg):
    p = premierAleatoire(inf, lg)
    if p == -1:
        return -1
    q = premierAleatoire(p + 1, lg + 1)
    if q == -1 or q == p:
        return -1
    phi = (p - 1) * (q - 1)
    e = premierAleatoireAvecRandom(phi)
    if e == -1:
        return -1
    return (p, q, e)

def clePublique(p, q, e):
    if p < 2 or q < 2 or e < 1:
        return -1
    n = p * q
    return (n, e)

def clePrivee(p, q, e):
    if p < 2 or q < 2 or e < 1:
        return -1
    phi = (p - 1) * (q - 1)
    if gcd(e, phi) != 1:
        return -1
    d = inverseModulaire(e, phi)
    if d == -1:
        return -1
    n = p * q
    return (n, d)

def codageRSA(M, n, e):
    if M >= n or M < 0:
        return -1
    return expoModulaire(M, e, n)

def decodageRSA(C, n, d):
    if C >= n or C < 0:
        return -1
    return expoModulaire(C, d, n)


""" if __name__ == "__main__":
    print(inverseModulaire(5, 298))
    print(estPremier(17))
    print(premierAleatoire(0, 100000000000000))
    print(premierAleatoireAvecRandom(15))
    print(premierAleatoireAvecRandom(12))
    p, q, e = choixCle(100, 500)
    print(f"choixCle -> p={p}, q={q}, e={e}")
    
    n_pub, e_pub = clePublique(p, q, e)
    print(f"Clé publique: (n={n_pub}, e={e_pub})")
    
    n_priv, d_priv = clePrivee(p, q, e)
    print(f"Clé privée: (n={n_priv}, d={d_priv})")
    
    M = 69
    C = codageRSA(M, n_pub, e_pub)
    print(f"Message original: {M}")
    print(f"Message codé: {C}")
    
    M_decoded = decodageRSA(C, n_priv, d_priv)
    print(f"Message décodé: {M_decoded}")
    print(f"Vérification: {M == M_decoded}") """