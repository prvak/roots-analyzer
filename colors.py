#!/usr/bin/python
# -*- coding: utf-8 -*-
import pygame # kresleni na obrazovku, klikani atp.
import os # pro prohledavani adresaru
import sys # zpracovani prikazove radky
import math # kvuli odmocnine

# nejprve definujeme nejake tridy, hlavni cast programu je na konci souboru
class SeznamSouboru:
    """Trida reprezentujici seznam souboru. """

    """Seznam podporovanych pripon souboru."""
    podporovanePripony = (".bmp", ".jpg", ".png")
    
    """Pozice pristiho jmena souboru, ktery bude vracen funkci 'dalsiSoubor()'."""
    pozice = -1

    """Seznam souboru s obrazky."""
    seznam = []

    def __init__(self, adresare):
        """Nacte seznam souboru v zadanych adresarich."""
        # projdeme vsechny adresare v seznamu ardesaru
        for adresar in adresare:
            self.nactiAdresar(adresar)

    def nactiAdresar(self, adresar):
        # pro kazdy adresar si zjistime seznam souboru
        seznamSouboru = os.listdir(adresar)
        # projdeme vsechny soubory a adresare v adresari a vyradime ty, ktere nas nezajimaji
        for soubor in seznamSouboru:
            # vyradime adresare a soubory se spatnou koncovkou
            if os.path.isfile(adresar+soubor):
                # 'soubor' neni adresar, chceme pouze soubory, ne adresare
                
                # zjistime koncovku souboru
                (jmeno, pripona) = os.path.splitext(soubor)

                # zmensime pismena, protoze 'BMP' je to same co 'bmp'
                pripona = pripona.lower()
                if pripona in self.podporovanePripony:
                    # soubor splnuje vsechny podminky, pridame ho do seznamu 
                    self.seznam.append(adresar+soubor)
        self.seznam = sorted(self.seznam)

    def poziceSouboru(self):
        """Vraci text 'pozice souboru/pocet souboru'."""
        return "%d/%d" % (self.pozice + 1, len(self.seznam))

    def tentoSoubor(self):
        """Vraci prave vybrany soubor."""
        if self.pozice >= 0 and self.pozice < len(self.seznam):
            # nejaky soubor existuje
            jmenoSouboru = self.seznam[self.pozice]
            return jmenoSouboru
        else:
            return ""
    
    def dalsiSoubor(self):
        """Vraci nasledujici soubor, pokud uz dalsi soubor neni, vraci prazdny retezec."""
        if self.jeKonec():
            # uz jsme na konci seznamu, vratime prazdny retezec
            return ""
        else:
            # jeste nejsme na konci seznamu
            self.pozice = self.pozice + 1
            jmenoSouboru = self.seznam[self.pozice]
            return jmenoSouboru
    
    def predchoziSoubor(self):
        """Vraci predchazejici soubor, pokud prave neni zobrazen prvni soubor."""
        if self.jeZacatek():
            # jsme na zacatku seznamu, vratime prazdny retezec
            return ""
        else:
            # jeste nejsme na zacatku seznamu
            self.pozice = self.pozice - 1
            jmenoSouboru = self.seznam[self.pozice]
            return jmenoSouboru

    def jeKonec(self):
        """Vraci True pokud je prave vybrany posledni soubor. Jinak vraci True."""
        if self.pozice == len(self.seznam) - 1:
            return True
        else:
            return False
    
    def jeZacatek(self):
        """Vraci True pokud je prave vybrany prvni soubor. Jinak vraci True."""
        if self.pozice <= 0:
            return True
        else:
            return False

class Cesta:
    def __init__(self, bod, barva, tloustka):
        self.barva = barva
        self.tloustka = tloustka
        self.body = [bod] # pocatecni bod cesty v puvodnim obrazku
        self.konec = False

    def pridej(self, bod):
        self.body.append(bod) # prida bod na konec cesty v puvodnim obrazku

    def ukonci(self):
        self.konec = True

    def ukoncena(self):
        return self.konec

    def vykresli(self, obrazek):
        #pygame.draw.lines(obrazek, self.barva, False, self.body, self.tloustka)
        for index in xrange(len(self.body) - 1):
            self._kresliUsek(obrazek, index)

    def vykresliPosledniUsek(self, obrazek):
        #pygame.draw.line(obrazek, self.barva, self.body[-2], self.body[-1], self.tloustka)
        self._kresliUsek(obrazek, len(self.body)-2)

    def _kresliUsek(self, obrazek, index):
        a = self.body[index]
        b = self.body[index + 1]
        dx = b[0] - a[0]
        dy = b[1] - a[1]
        lx = abs(dx)
        ly = abs(dy)
        l = max(lx, ly)
        if l > 0:
            for bod in [(int(a[0]+1.0*n*dx/l), int(a[1]+1.0*n*dy/l)) for n in xrange(l)]:
                pygame.draw.circle(obrazek, self.barva, bod, self.tloustka/2, 0)
        else:
            # oba body maji stejne souradnice
            pygame.draw.circle(obrazek, self.barva, a, self.tloustka/2, 0)
            

class Tlacitko:
    def __init__(self, nazev, barva, barva2, udalost, sTextem = True):
        self.nazev = nazev
        self.barva = pygame.Color(barva)
        self.barva2 = pygame.Color(barva2)
        self.udalost = udalost
        self.sTextem = sTextem
        self.obdelnik = None
        self.vybrane = False
        self.oznacene = False
        self.skupina = None
    
    def jeNaPozici(self, bod):
        if self.obdelnik:
            return self.obdelnik.collidepoint(bod)
        return False

    def seskup(self, skupina):
        self.skupina = skupina

    def zmackni(self):
        if self.skupina:
            for t in self.skupina:
                t.vyber(False)
            self.vyber(True) # pouze seskupena tlacitka mohou byt vybrana
        self._posliUdalost()

    def vyber(self, vybrane):
        self.vybrane = vybrane
        self._prekresli()
    
    def oznac(self, oznacene):
        self.oznacene = oznacene
        self._prekresli()

    def kresli(self, okno, obdelnik):
        """Nakresli tlacitko do okna 'okno' do obdelniku 'obdelnik'."""
        self.obdelnik = obdelnik
        self.okno = okno
        self._prekresli()

    def _prekresli(self):
        ramecek = pygame.Color(0x00000000)
        pozadi = self.barva
        if self.oznacene:
            pozadi = self.barva2
        if self.vybrane or self.oznacene:
            ramecek = pygame.Color(0xedd53300)
        #pygame.draw.rect(self.okno, pozadi, self.obdelnik) # pozadi
        self.okno.fill(pozadi, self.obdelnik) # pozadi
        pygame.draw.rect(self.okno, ramecek, self.obdelnik, 2) # ramecek
        if self.sTextem:
            text = font.render(self.nazev, True, ramecek)
            obdelnikTextu = text.get_rect()
            obdelnikTextu.center = self.obdelnik.center
            self.okno.blit(text, obdelnikTextu)
        pygame.display.update(self.obdelnik) # zobrazime provedenou zmenu 
     
    def _posliUdalost(self):
        udalost = pygame.event.Event(pygame.USEREVENT, code=self.udalost)
        pygame.event.post(udalost)

class TlacitkoBarvy(Tlacitko):
    def __init__(self, nazev, barva, barva2):
        Tlacitko.__init__(self, nazev, barva, barva2, "barva", False)
     
    def _posliUdalost(self):
        udalost = pygame.event.Event(pygame.USEREVENT, code=self.udalost, color=self.barva)
        pygame.event.post(udalost)
        

class Menu:
    def __init__(self):
        with open("colors.cfg") as f:
            f.readline() # first line contains headers, ignore it
            lines = f.readlines()
        
        self.barvy = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            (nazev, barva, zbytek) = line.split(";", 2) # zajimaji nas pouze prvni dva sloupce
            tlacitko = TlacitkoBarvy(nazev, int(barva+"00", 16), int(barva+"55", 16))
            self.barvy.append(tlacitko)
        self.barvy.append(TlacitkoBarvy("Bila", "0xffffff00", "0xffffff55"))
        self.tloustky = []
        self.tloustky.append(Tlacitko(u"Tlustá", 0xffffff00, 0xdddddd00, "tlusta"))
        self.tloustky.append(Tlacitko(u"Tenká", 0xffffff00, 0xdddddd00, "tenka"))
#        self.barvy = [
#                TlacitkoBarvy("Modra", 0x4b60f900, 0x3648ca00),
#                TlacitkoBarvy("Cervena", 0xe3042000, 0xac303f00),
#                TlacitkoBarvy("Zelena", 0x1e981d00, 0x2a7e2900),
#                TlacitkoBarvy("Oranzova", 0xef8a0000, 0xda7e0000),
#                TlacitkoBarvy("Ruzova", 0xdf4bc700, 0xdf1fc000),
#                TlacitkoBarvy("Fialova", 0x76269900, 0x9d35ca00),
#                TlacitkoBarvy("Cerna", 0x00000000, 0x11111100),
#                TlacitkoBarvy("Hneda", 0x955a0900, 0x99692600),
#                TlacitkoBarvy("Zluta", 0xe8da0200, 0xd5ca1700),
#                TlacitkoBarvy("Bila", 0xffffff00, 0xdddddd00)
#            ] # tlacitka barev, vzdy je prave jedno z nich vybrane
        self.tlacitka = []
        self.tlacitka.extend(self.barvy)
        self.tlacitka.extend(self.tloustky)
        self.tlacitka.append(Tlacitko(u"Zpět", 0xffffff00, 0xdddddd00, "zpet"))
        self.tlacitka.append(Tlacitko("+", 0xffffff00, 0xdddddd00, "+"))
        self.tlacitka.append(Tlacitko("-", 0xffffff00, 0xdddddd00, "-"))
        self.tlacitka.append(Tlacitko(u"Další", 0xffffff00, 0xdddddd00, "dalsi"))
        for t in self.barvy:
            t.seskup(self.barvy)
        for t in self.tloustky:
            t.seskup(self.tloustky)
        self.barvy[0].vybrane = True
        self.tloustky[0].vybrane = True
        self.obdelnik = None # obdelnik, ve kterem je menu vykresleno

    def klik(self, bod):
        """Provede akci po stisknuti tlacitka na pozici 'bod'.
        Vraci True, pokud bylo kliknuto na nejake tlacitko, jinak vraci False."""
        return False

    def tlacitkoNaPozici(self, bod):
        if self.tlacitka:
            for t in self.tlacitka:
                if t.jeNaPozici(bod):
                    return t
        return None

    def kresli(self, okno):
        """Vykresli menu do okna 'okno'."""
        # spocitame obdelnik, ve kterem bude menu vykresleno
        o = okno.get_rect()
        s = 80
        self.obdelnik = pygame.Rect(o.width - s, 0, s, o.height)
        # vykreslime menu
        pocet = len(self.tlacitka)
        if pocet > 0:
            v = self.obdelnik.height/pocet # vyska jednoho tlacitka
            x = self.obdelnik.left # vzdalenost tlacitka od leveho okraje
            for i in xrange(pocet):
                y = i*v
                tlacitko = self.tlacitka[i]
                obdelnikTlacitka = pygame.Rect(x, y, s, v)
                tlacitko.kresli(okno, obdelnikTlacitka)

class Manazer:
    def __init__(self, menu, okno, soubory):
        self.okno = okno # okno do ktereho bude obrazek vykreslen
        self.menu = menu # menu, ktere bude vykresleno pres obrazek
        self.soubory = soubory # manazer souboru
        self.barva = menu.barvy[0].barva # vybrana barva
        self.tlusta()
        self.priblizeni = 1 
        self.barvaPozadi = pygame.Color(0x12670b00)
    def nacti(self, predchozi = False):
        if predchozi:
            soubor = self.soubory.predchoziSoubor()
        else:
            soubor = self.soubory.dalsiSoubor()
        if not soubor:
            print "No more files. Exiting."
            return False
        print "Loading file '%s'" % (soubor)
        self.obrazek = nactiObrazek(soubor) # original obrazku
        self.zmeneny = self.obrazek.copy() # obrazek vcetne vsech zmen
        self.priblizeny = self.obrazek.copy() # obrazek v aktualnim priblizeni a se zmenami
        self.cesty = [] # cesty, ktere jiz byly do obrazku zakresleny
        self.cestyOdebrane = []
        # kolika zobrazenym pixelum odpovida 1 pixel originalniho obrazku, 
        # musi byt cele cislo vetsi nez 0
        self.posunuti = (0, 0)
        self._prekresli()
        return True

    def uloz(self):
        soubor = self.soubory.tentoSoubor()
        if self.cesty:
            print "Saving file '%s'" % (soubor)
            pygame.image.save(self.zmeneny, self.soubory.tentoSoubor())
        else:
            print "No changes in file '%s'" % (soubor)

    def tenka(self):
        self.tloustka = 2
    
    def tlusta(self):
        self.tloustka = 8
    
    def zvets(self):
        self.priblizeni = self.priblizeni + 1
        if self.priblizeni > 8:
            self.priblizeni = 8
        velikost = [x*self.priblizeni for x in self.zmeneny.get_size()]
        self.priblizeny = pygame.transform.scale(self.zmeneny, velikost)
        self._prekresli()

    def zmensi(self):
        self.priblizeni = self.priblizeni - 1
        if self.priblizeni <= 1:
            self.priblizeni = 1
        velikost = [x*self.priblizeni for x in self.zmeneny.get_size()]
        self.priblizeny = pygame.transform.scale(self.zmeneny, velikost)
        self._prekresli()

    def nastavBarvu(self, barva):
        self.barva = barva

    def posun(self, posunuti):
        self.posunuti = [sum(x) for x in zip(self.posunuti, posunuti)]
        self._prekresli()

    def kresli(self, bod, konec = False):
        bod2 = [int((x[0]-x[1])/self.priblizeni) for x in zip(bod, self.posunuti)]
        if not self.cesty or self.cesty[-1].ukoncena():
            # neexistuje zatim zadna cesta, nebo posledni cesta je jiz ukoncena
            # vytvor novou cestu s timto bodem
            cesta = Cesta(bod2, self.barva, self.tloustka)
            self.cesty.append(cesta)
        else:
            # jinak vezmi posledni cestu
            cesta = self.cesty[-1]
        if konec:
            # ukonci aktualni cestu
            cesta.ukonci()
        bod1 = cesta.body[-1]
        # najdi obdelnik, do ktereho se vejdou vsechny zmenene pixely
        # zvetsime a prekreslime pouze tento obdelnik, aby se nemusel
        # zvetsovat cely obrazek
        t = cesta.tloustka
        vrchol = [min(x)-t for x in zip(bod1,bod2)] # levy horni roh obdelniku vyrezu
        rozmery = [abs(x[1] - x[0])+3*t for x in zip(bod1, bod2)] # rozmery vyrezu
        obdelnikVyrezu = pygame.Rect(vrchol, rozmery)
        obdelnikObrazku = self.zmeneny.get_rect()
        obdelnikVyrezu = obdelnikVyrezu.clamp(obdelnikObrazku)
        if self.menu.tlacitkoNaPozici(bod) or not obdelnikObrazku.contains(obdelnikVyrezu):
            # kresleno mimo obrazek, ukonci aktualni cestu, aby nedoslo k nakresleni
            # dlouhe cary v pripade, ze se kurzor vrati zpet do obrazku
            cesta.ukonci()
            if len(cesta.body) == 1:
                # tato cesta obsahuje pouze jediny bod a to ten, ktery je zcela mimo
                # obrazek, odeber cestu
                self.cesty.pop()
            return # nedojde k zadnemu prekresleni
        cesta.pridej(bod2)
        # nakresli caru do zmeneneho obrazku
        cesta.vykresliPosledniUsek(self.zmeneny)
        # vyrizni dotceny obdelnik ze zmeneneho obrazku v originalni velikosti
        vyrez = self.zmeneny.subsurface(obdelnikVyrezu)
        # zvets nebo zmensi vyrez na aktualni priblizeni
        vrchol = obdelnikVyrezu.topleft
        priblizenyVrchol = [x*self.priblizeni for x in vrchol]
        rozmery = obdelnikVyrezu.size
        priblizeneRozmery = [x*self.priblizeni for x in rozmery]
        priblizenyVyrez = pygame.transform.scale(vyrez, priblizeneRozmery)
        # prekresli prislusnou cast v aktualnim obrazku transformovanym vyrezem
        self.priblizeny.blit(priblizenyVyrez, priblizenyVrchol) # vlozime obrazek do okna
        self._prekresli(priblizenyVyrez.get_rect())

    def zpet(self):
        if not self.cesty:
            return
        self.cesty.pop()
        self.zmeneny = self.obrazek.copy()
        for c in self.cesty:
            c.vykresli(self.zmeneny)
        velikost = [x*self.priblizeni for x in self.zmeneny.get_size()]
        self.priblizeny = pygame.transform.scale(self.zmeneny, velikost)
        self._prekresli()

    def vpred(self):
        pass

    def _prekresli(self, vyrez = None):
        # ziskame sirku a vysku okna a obrazku
        obdelnikOkna = self.okno.get_rect()
        if not vyrez:
            vyrez = obdelnikOkna
        obdelnikObrazku = self.priblizeny.get_rect().move(self.posunuti[0], self.posunuti[1])
        # vyplnime celou obrazovku barvou pozadi
        pygame.draw.rect(okno, self.barvaPozadi, vyrez)
        
        # vykreslime obrazek na obrazovku
        okno.blit(self.priblizeny, obdelnikObrazku) # vlozime obrazek do okna
        
        # vypiseme nazev souboru
        text = font.render(self.soubory.poziceSouboru()+": "+self.soubory.tentoSoubor(), True, pygame.Color(0x00000000))
        obdelnikTextu = text.get_rect()
        obdelnikTextu.topleft = obdelnikOkna.topleft
        self.okno.blit(text, obdelnikTextu)
        
        # vykreslime menu
        self.menu.kresli(okno)
        # zobrazime provedenou zmenu 
        pygame.display.update() 
    

# dale definujeme nejake funkce
def vytvorOkno():
    """Pripravi okno programu. Vraci objekt reprezentujici toto okno."""

    # inicializace obrazovky, tj. mista, kam budeme kreslit,
    # muze zabirat bud celou obrazovku, nebo to bude jenom okno
    pygame.init()
    pygame.display.init()
    #pygame.mouse.set_visible(False)
    #okno = pygame.display.set_mode((800,600), pygame.FULLSCREEN|pygame.DOUBLEBUF|pygame.HWSURFACE) # sice fullscreen, ale kresli jen doprostred
    okno = pygame.display.set_mode((0,0), pygame.FULLSCREEN|pygame.DOUBLEBUF|pygame.HWSURFACE) # pravy fulscreen
    #okno = pygame.display.set_mode((800,600), pygame.DOUBLEBUF|pygame.HWSURFACE) # okno o danych rozmerech

    # povoleni udalosti mysi a klavesnice
    # kdyz zmackneme tlacitko, pohneme mysi atp., tak se o tom program dozvi
    pygame.event.set_allowed(pygame.MOUSEBUTTONDOWN)
    pygame.event.set_allowed(pygame.KEYDOWN)
    
    # vratime objekt reprezentujici okno
    return okno

def nactiObrazek(cestaSouboru):
    """Nacte obrazek ze souboru 'cestaSouboru' a vrati objekt reprezentujici tento
    obrazek."""
    obrazek = pygame.image.load(cestaSouboru).convert()
    return obrazek

def nakresliObrazekZeSouboru(cestaSouboru, okno, databaze, vybraneBody):
    jmenoSouboru = os.path.split(cestaSouboru)[1] # zajima nas jen jmeno souboru, ne adresar
    hashSouboru = 0
    if databaze.zaznamy.has_key(jmenoSouboru):
        zaznam = databaze.zaznamy[jmenoSouboru]
    else:
        # zaznam pro tento obrazek jeste v databazi neni
        # vytvorime novy prazdny zaznam a dame ho do databaze
        zaznam = Zaznam()
        zaznam.nastav(jmenoSouboru, hashSouboru)
        databaze.zaznamy[jmenoSouboru] = zaznam
    obrazek = nactiObrazek(cestaSouboru)
    (x0, y0, sirkaObrazku, vyskaObrazku, pomer) = nakresliObrazek(obrazek, okno)
    pygame.display.set_caption(cestaSouboru)
    vybraneBody.nactiBody(okno, zaznam, pomer, x0, y0)
    pygame.display.flip() # zobrazime provedenou zmenu 
    return (x0, y0, sirkaObrazku, vyskaObrazku, pomer, zaznam)

def zobrazDalsiObrazek(seznamSouboru, okno, databaze, vybraneBody):
    """Zobrazi dalsi obrazek a vrati souradnice leveho horniho rohu a sirku a vysku obrazku. 
    Seznam souboru nesmi byt na konci."""
    cestaSouboru = seznamSouboru.dalsiSoubor()
    return nakresliObrazekZeSouboru(cestaSouboru, okno, databaze, vybraneBody)

def zobrazPredchoziObrazek(seznamSouboru, okno, databaze, vybraneBody):
    """Zobrazi predchozi obrazek a vrati souradnice leveho horniho rohu a sirku a vysku obrazku. 
    Seznam souboru nesmi byt na zacatku."""
    cestaSouboru = seznamSouboru.predchoziSoubor()
    return nakresliObrazekZeSouboru(cestaSouboru, okno, databaze, vybraneBody)

def pouziti():
    """Vypise co se ma napsat na prikazovou radku, aby program fungoval."""
    print "Usage: analyze.py DIRECTORY"
    print "    DIRECTORY Directory with images to analyze."



# uz mame definovane vsechny funkce a objekty a ted je budeme pouzivat

# zkontrolujeme, ze byl zadan alespon jeden parametr na prikazove radce
if len(sys.argv) <= 1:
    # nebyl zadan zadny adresar
    print "Missing arguments."
    exit()
elif len(sys.argv) >= 3:
    # nebyl zadan zadny adresar
    print "Too many arguments."
    exit()

# ziskame adresar z prikazove radky
adresar = sys.argv[1]
if adresar[-1] != '/':
    # doplnime lomitko na konec adresare, ale jen pokud tam uz neni
    adresar = adresar + '/'

# nacteme seznam soubor
if not os.path.isdir(adresar):
    # nebyl zadan adresar, ale neco jineho
    print "Not a directory:"
    print adresar
    exit()

seznamSouboru = SeznamSouboru([adresar]) 
if seznamSouboru.jeKonec():
    # v zadanych adresarich neni zadny pripustny soubor
    print "No acceptable files in directory:"
    print adresar
    exit()

# vytvorime okno programu
okno = vytvorOkno()

font = pygame.font.Font("DejaVuSans-Bold.ttf", 15)
menu = Menu()
manazer = Manazer(menu, okno, seznamSouboru)

# nacteme a nakreslime prvni obrazek vcetne vybranych bodu
manazer.nacti()
drzenoZa = None
kreslenoOd = None
tlacitko = None
while(1):
    # nekonecny cyklus, ktery zpracovava udalosti
    udalost = pygame.event.wait()
    if udalost.type==pygame.MOUSEBUTTONDOWN:
        if udalost.button == 1:
            # 1 == kliknuto levym tlacitkem
            manazer.kresli(udalost.pos) # zacatek cary
            kreslenoOd = udalost.pos
        elif udalost.button == 2:
            # 2 == kliknuto prostrednim tlacitkem
            drzenoZa = udalost.pos
    elif udalost.type==pygame.MOUSEBUTTONUP:
        if udalost.button == 1:
            manazer.kresli(udalost.pos, True)
            kreslenoOd = None
            t = menu.tlacitkoNaPozici(udalost.pos)
            if t and tlacitko:
                # mys je nad tlacitkem
                tlacitko.zmackni()
                tlacitko = t
            else:
                tlacitko = None
        elif udalost.button == 2:
            if drzenoZa and drzenoZa != udalost.pos:
                manazer.posun([x[1] - x[0] for x in zip(drzenoZa, udalost.pos)])
            drzenoZa = None
    elif udalost.type==pygame.MOUSEMOTION:
        if drzenoZa:
            # s obrazkem je prave hybano
            manazer.posun([x[1] - x[0] for x in zip(drzenoZa, udalost.pos)])
            drzenoZa = udalost.pos
        elif kreslenoOd:
            manazer.kresli(udalost.pos) # pokracovani cary
            kreslenoOd = udalost.pos
        else:
            t = menu.tlacitkoNaPozici(udalost.pos)
            if t:
                # mys je nad tlacitkem
                if tlacitko != t:
                    if tlacitko:
                        tlacitko.oznac(False)
                    t.oznac(True)
                tlacitko = t
            else:
                if tlacitko:
                    tlacitko.oznac(False)
                tlacitko = None
                # kresli jen pokud nejsme nad tlacitkem
    elif udalost.type == pygame.USEREVENT:
        if udalost.code == "barva":
            manazer.nastavBarvu(udalost.color)
        elif udalost.code == "tenka":
            manazer.tenka()
        elif udalost.code == "tlusta":
            manazer.tlusta()
        elif udalost.code == "zpet":
            manazer.zpet()
        elif udalost.code == "dalsi":
            manazer.uloz()
            if not manazer.nacti():
                exit()
        elif udalost.code == "+":
            manazer.zvets()
        elif udalost.code == "-":
            manazer.zmensi()
    
    elif udalost.type == pygame.KEYDOWN:
        # zmacknuta klavesa
        if udalost.key == pygame.K_RIGHT:
            # sipka doprava => zobraz dalsi obrazek
            manazer.uloz()
            if not manazer.nacti():
                exit()
        if udalost.key == pygame.K_LEFT:
            # sipka doprava => zobraz dalsi obrazek
            manazer.uloz()
            if not manazer.nacti(True): # True == nacti predchozi soubor misto nasledujiciho
                exit()
        elif udalost.key == pygame.K_ESCAPE:
            # esc => ukonci program
            manazer.uloz()
            exit()
        else:
            # ostatni klavesy ignorujeme
            pass
    elif udalost.type == pygame.QUIT:
        # ukonceni aplikace krizkem
        manazer.uloz()
        exit()

