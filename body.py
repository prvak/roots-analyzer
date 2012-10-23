#!/usr/bin/python
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




class VybranyBod:
    """Trida pro zobrazeni vybraneho bodu."""

    """Prumer kruznice v pixelech."""
    polomer = 15

    """Tloustka cary kruznice."""
    tloustka = 1
    
    """Delka cary stredoveho krize."""
    delka = polomer/3
    
    """Kolik pixelu od stredu obrazku bude koncit kazda cara. To ma ten efekt, ze
    vybrany bod nebude prekresleny stredovymm krizem."""
    mezera = 3

    def __init__(self, barva):
        # nove vytvoreny bod je skryty
        self.zobrazen = False
        # pozice je na pocatku 0,0, bude nastavena po kliknuti mysi, pozice urcuje stred obrazku
        self.pozice = (0, 0)
        # krome pozice si budeme pamatovat i ohraniceni obrazku, tj. obdelnik ve kterem je obrazek nakreslen
        r = VybranyBod.polomer
        self.ohraniceni = pygame.Rect(-r, -r, r*2, r*2)
        # bod je vyznacen obrazkem kruznice
        self.obrazek = pygame.Surface((VybranyBod.polomer*2, VybranyBod.polomer*2))
        self.obrazek.set_colorkey(0x000000) # nastavi cernou barvu jako pruhlednou
        # nakresli stredovy kriz
        pygame.draw.line(self.obrazek, barva, (VybranyBod.polomer - VybranyBod.delka, VybranyBod.polomer), (VybranyBod.polomer - VybranyBod.mezera, VybranyBod.polomer))
        pygame.draw.line(self.obrazek, barva, (VybranyBod.polomer + VybranyBod.delka, VybranyBod.polomer), (VybranyBod.polomer + VybranyBod.mezera, VybranyBod.polomer))
        pygame.draw.line(self.obrazek, barva, (VybranyBod.polomer, VybranyBod.polomer - VybranyBod.delka), (VybranyBod.polomer, VybranyBod.polomer - VybranyBod.mezera))
        pygame.draw.line(self.obrazek, barva, (VybranyBod.polomer, VybranyBod.polomer + VybranyBod.delka), (VybranyBod.polomer, VybranyBod.polomer + VybranyBod.mezera))
        # nakresli kruznici
        pygame.draw.circle(self.obrazek, barva, (VybranyBod.polomer, VybranyBod.polomer), VybranyBod.polomer, VybranyBod.tloustka)
        # aby se dal bod snadno presouvat a nebylo treba prekreslovat cele okno,
        # ulozime si pred vykreslenim bodu jeho podklad, timto podkladem bude
        # bod prekreslen pri presouvani
        self.pozadi = pygame.Surface((VybranyBod.polomer*2, VybranyBod.polomer*2))

    def zobraz(self, okno, pozice):
        """Nakresli tento bod do zadaneho okna a na zadanou pozici."""
        if not self.zobrazen:
            # zmenime pozici obrazku
            self.pozice = pozice
            self.ohraniceni.topleft = [pozice[0] - VybranyBod.polomer, pozice[1] - VybranyBod.polomer] 
            # ulozime pozadi obrazku
            self.pozadi.blit(okno, self.pozadi.get_rect(), self.ohraniceni)
            # nakreslime obrazek na danou pozici
            okno.blit(self.obrazek, self.ohraniceni)
            self.zobrazen = True
        else:
            raise "Can not display already visible point!"
    
    def prekresli(self, okno, pozice):
        """Nakresli tento bod do zadaneho okna a na zadanou pozici."""
        if self.zobrazen:
            # nejprve prekreslime posledni pozici pozadim
            okno.blit(self.pozadi, self.ohraniceni)
            # zmenime pozici obrazku
            self.pozice = pozice
            self.ohraniceni.topleft = [pozice[0] - VybranyBod.polomer, pozice[1] - VybranyBod.polomer] 
            # ulozime pozadi obrazku
            self.pozadi.blit(okno, self.pozadi.get_rect(), self.ohraniceni)
            # nakreslime obrazek na novou pozici
            okno.blit(self.obrazek, self.ohraniceni)
        else:
            raise "Can not redraw point that is not visible."
        
    def skryj(self, okno):
        """Skryj jiz zobrazeny bod."""
        if self.zobrazen:
            # prekreslime posledni pozici pozadim
            okno.blit(self.pozadi, self.ohraniceni)
            self.zobrazen = False
        else:
            raise "Can not hide already hidden point!"

    def jePoziceBlizkoBodu(self, pozice):
        x1, y1 = self.pozice
        x2, y2 = pozice
        if math.sqrt((x2 - x1)**2 + (y2 - y1)**2) < VybranyBod.polomer:
            # pozice je od stredu kruznice blize nez jeji polomer => pozice je uvnitr kruznice
            return True
        else:
            return False

    def vzdalenostOdStredu(self, pozice):
        """Vraci o kolik pixelu je pozice vzdalena od stredu obrazku. 
        To se hodi pro ucely presouvani bodu tazenim. Kdyz je obrazek chycen za jine misto
        nez za stred, tak je jeho nova pozice pocitana ne podle pozice mysi, ale podle pozice mysi
        posunute o vzdalenost vracenou touto funkci. To zabranuje poskoceni obrazku v prvnim 
        okamziku jeho presouvani."""
        x1, y1 = self.pozice
        x2, y2 = pozice
        return (x2-x1, y2-y1)

class VybraneBody:
    def __init__(self):
        # vytvor 
        self.body = []
        self.body.append(VybranyBod(0xff0000))
        self.body.append(VybranyBod(0x00ff00))
        self.body.append(VybranyBod(0x0000ff))
        self.body.append(VybranyBod(0xffff00))

    def nactiBody(self, okno, zaznam, pomer, x0, y0):
        """Nacte body z daneho zaznamu a zobrazi je v okne."""
        self.reset()
        for (pozice, bod) in zip(zaznam.body, self.body):
            if pozice != (-1, -1):
                # prepocitej souradnice bodu v obrazku na souradnice bodu na obrazovce
                x, y = pozice # pozice v obrazku
                x = x*pomer + x0
                y = y*pomer + y0
                bod.zobraz(okno, (x,y))

    def pridejBod(self, okno, pozice):
        for bod in self.body:
            if not bod.zobrazen:
                # nasli jsme bod, ktery jeste neni zobrazen, zobrazime ho
                bod.zobraz(okno, pozice)
                break # dalsi body uz nepridavej
    
    def odeberBod(self, okno, pozice):
        """Odebere bod, ktery se nachazi pobliz zadane pozice."""
        vybranyBod = self.bodNaPozici(pozice)
        if vybranyBod != None:
            # byl vybran nejaky bod, pokud se dva body prekryvaji, je vybran ten, 
            # ktery je v seznamu blize ke konci
            vybranyBod.skryj(okno)

    def bodNaPozici(self, pozice):
        """Vrati zobrazeny bod na pozici 'pozice' (nebo pobliz)."""
        vybranyBod = None
        for bod in self.body:
            if bod.zobrazen:
                # nasli jsme bod, ktery je zobrazen => muzeme ho ubrat
                # jeste potrebujeme, aby byl na dane pozici
                if bod.jePoziceBlizkoBodu(pozice):
                    vybranyBod = bod
        return vybranyBod
    
    def reset(self):
        """Skryje vsechny body, ale neprekresli okno. Bude pouzito pri prepinani obrazku."""
        for bod in self.body:
            bod.zobrazen = False
        
        
class Zaznam:
    """Trida reprezentujici jeden zaznam v databazi."""
   
    @staticmethod
    def hlavicka():
        """Vraci retezec s nadpisy jednotlivych zaznamu."""
        return "#jmeno,hash,x0,y0,x1,y1,x2,y2,x3,y3"

    def __init__(self):
        self.soubor = ""
        self.hash = 0
        self.body = [(-1,-1), (-1,-1), (-1,-1), (-1,-1)] # -1,-1 znaci, ze dany bod neni inicializovany

    def nastav(self, souborObrazku, hashObrazku):
        self.soubor = souborObrazku
        self.hash = hashObrazku # slouzi k rozpoznani toho, ze se soubor zmenil
        self.body = [(-1,-1), (-1,-1), (-1,-1), (-1,-1)] # -1,-1 znaci, ze dany bod neni inicializovany

    def nacti(self, radek):
        sloupce = radek.split(",")
        if len(sloupce) == 10:
            # mame presne 10 sloupcu, to je dobre
            self.soubor = os.path.split(sloupce[0])[1] # ignoruj adresar
            self.hash = int(sloupce[1])
            for i in xrange(4):
                x = int(sloupce[2 + i*2])
                y = int(sloupce[2 + i*2 + 1])
                self.body[i] = ((x,y))

    def uloz(self):
        radek = "%s,%d" % (self.soubor, self.hash)
        for bod in self.body:
            radek = radek + ",%d,%d" % bod
        return radek

    def nastavBody(self, vybraneBody, pomer, x0, y0):
        poradi = 0 # poradi bodu v seznamu
        for bod in vybraneBody.body:
            if bod.zobrazen:
                # prepocitej souradnice bodu na obrazovce na souradnice v obrazku
                # pokud byl obrazek zmensen, tak prevod neni jednoznacny, ale par pixelu sem nebo tam
                # by nemelo hrat roli
                x, y = bod.pozice
                x = (x-x0)/pomer
                y = (y-y0)/pomer
                self.body[poradi] = (x,y)
            else:
                self.body[poradi] = (-1,-1)
            poradi = poradi + 1


class Databaze:
    """Databaze zaznamu k ruznym obrazkum."""

    def __init__(self, jmenoSouboru):
        """Vytvori novou databazi v zadanem souboru, nebo nacte existujici databazi z tohoto souboru."""
        self.zaznamy = {}
        self.jmenoSouboru = jmenoSouboru
        if os.path.exists(jmenoSouboru) and os.path.isfile(jmenoSouboru):
            # nacti zaznamy ze souboru
            print "Loading database file: " + jmenoSouboru
            self.nacti()
        else:
            # vytvor prazdny soubor pouze s hlavickou
            print "Creating database file: " + jmenoSouboru
            soubor = open(self.jmenoSouboru, "w")
            radek = Zaznam.hlavicka() + "\n"
            soubor.write(radek)
            soubor.close()

    def nacti(self):
        soubor = open(self.jmenoSouboru)
        radky = soubor.readlines()
        soubor.close()
        for radek in radky:
            radek = radek.strip()
            if len(radek) > 0 and radek[0] != "#":
                # ignoruj prazdne radky a radky zacinajici mrizkou
                zaznam = Zaznam()
                zaznam.nacti(radek)
                self.zaznamy[zaznam.soubor] = zaznam

    def uloz(self):
        soubor = open(self.jmenoSouboru, "w")
        radek = Zaznam.hlavicka() + "\n"
        soubor.write(radek)
        klice = sorted(self.zaznamy.keys())
        for klic in klice:
            radek = self.zaznamy[klic].uloz() + "\n"
            soubor.write(radek)
        soubor.close()

    
# dale definujeme nejake funkce
def vytvorOkno():
    """Pripravi okno programu. Vraci objekt reprezentujici toto okno."""

    # inicializace obrazovky, tj. mista, kam budeme kreslit,
    # muze zabirat bud celou obrazovku, nebo to bude jenom okno
    pygame.init()
    pygame.display.init()
    #okno = pygame.display.set_mode((800,600), pygame.FULLSCREEN|pygame.DOUBLEBUF|pygame.HWSURFACE) # sice fullscreen, ale kresli jen doprostred
    #okno = pygame.display.set_mode((0,0), pygame.FULLSCREEN|pygame.DOUBLEBUF|pygame.HWSURFACE) # pravy fulscreen
    okno = pygame.display.set_mode((800,600), pygame.DOUBLEBUF|pygame.HWSURFACE) # okno o danych rozmerech

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

def nakresliObrazek(obrazek, okno):
    """Nakresli obrazek 'obrazek' do okna 'okno'. Vraci souradnice leveho horniho 
    rohu obrazku a sirku a vysku nakresleneho obrazku (ta muze byt vetsi nebo mensi 
    nez puvodni rozmery obrazku) a pomer velikosti puvodniho a zmeneneho obrazku.
    pomer mensi nez 1 znamena, ze puvodni obrazek byl vetsi nez zobrazeny obrazek."""
    
    # ziskame sirku a vysku okna a obrazku
    sirkaOkna, vyskaOkna = okno.get_size()
    sirkaObrazku,vyskaObrazku = obrazek.get_size()

    # spocitame, jake rozmery by mel mit obrazek, aby se vesel na obrazovku
    #print "%dx%d -> %dx%d" % (sirkaObrazku,vyskaObrazku,sirkaOkna,vyskaOkna)
    if float(sirkaOkna)/sirkaObrazku > float(vyskaOkna)/vyskaObrazku:
        pomer = float(vyskaOkna)/vyskaObrazku  # float znaci, ze se bude provadet deleni s desetinnou carkou, jinak by slo o celociselne deleni
        sirkaObrazku = sirkaObrazku*vyskaOkna/vyskaObrazku
        vyskaObrazku = vyskaOkna
        x0 = (sirkaOkna-sirkaObrazku)/2
        y0 = 0
    else:
        pomer = float(sirkaOkna)/sirkaObrazku
        vyskaObrazku = vyskaObrazku*sirkaOkna/sirkaObrazku
        sirkaObrazku = sirkaOkna
        y0 = (vyskaOkna-vyskaObrazku)/2
        x0 = 0
    #print " => %dx%d"%(sirkaObrazku,vyskaObrazku)
    
    # zmenime velikost obrazku tak, aby se vesel na obrazovku (nejcasteji pujde o zmenseni, ale muze se i zvetsit)
    zmenenyObrazek = pygame.transform.scale(obrazek, (sirkaObrazku,vyskaObrazku))

    # vyplnime celou obrazovku cernou barvou
    obdelnikCelehoOkna = pygame.Rect(0, 0, sirkaOkna, vyskaOkna)
    pygame.draw.rect(okno, 0x424242, obdelnikCelehoOkna)
    
    # vykreslime obrazek na obrazovku
    obdelnikObrazku = pygame.Rect(0, 0, sirkaObrazku, vyskaObrazku) # jakou cast obrazku zobrazime (v tomto pripade cely obrazek)
    obdelnikOkna = pygame.Rect(x0, y0, sirkaObrazku, vyskaObrazku) # kam do okna umistime obrazek
    okno.blit(zmenenyObrazek, obdelnikOkna, obdelnikObrazku) # vlozime obrazek do okna
    
    # vratime sirku a vysku zmeneho obrazku
    return (x0, y0, sirkaObrazku, vyskaObrazku, pomer)

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

# nacteme nebo vytvorime databazi
databaze = Databaze(adresar[:-1]+".csv")

# vytvorime seznam bodu
body = VybraneBody()

# nacteme a nakreslime prvni obrazek vcetne vybranych bodu
(x0, y0, sirkaObrazku, vyskaObrazku, pomer, zaznam) = zobrazDalsiObrazek(seznamSouboru, okno, databaze, body)

presouvanyBod = None
presouvanyBodDrzenZa = (0, 0) # vzdalenost bodu, za ktery je presouvany obrazek drzen od stredu obrazku
bodPresunut = False
while(1):
    # nekonecny cyklus, ktery zpracovava udalosti
    udalost = pygame.event.wait()
    if udalost.type==pygame.MOUSEBUTTONDOWN:
        if udalost.button == 1:
            # 1 == kliknuto levym tlacitkem
            presouvanyBod = body.bodNaPozici(udalost.pos)
            if presouvanyBod != None:
                presouvanyBodDrzenZa = presouvanyBod.vzdalenostOdStredu(udalost.pos)
            bodPresunut = False
        elif udalost.button == 3:
            # 3 == kliknuto pravym tlacitkem
            body.odeberBod(okno, udalost.pos)
            pygame.display.flip()
    elif udalost.type==pygame.MOUSEBUTTONUP:
        if udalost.button == 1 and (presouvanyBod == None or bodPresunut == False):
            # nebylo kliknuto na zadny bod nebo sice bylo kliknuto na nejaky
            # bod, ale ten nebyl presunut 
            x,y = udalost.pos
            if (x >= x0 and x <= x0 + sirkaObrazku) and (y >= y0 and y <= y0 + vyskaObrazku):
                # ignoruj kliknuti mimo obrazek
                #print "Click: %d,%d" % (x,y)
                body.pridejBod(okno, (x,y))
                pygame.display.flip()
        presouvanyBod = None
    elif udalost.type==pygame.MOUSEMOTION:
        if presouvanyBod != None:
            x, y = udalost.pos
            x1, y1 = presouvanyBodDrzenZa
            if (x - x1 >= x0 and x - x1 <= x0 + sirkaObrazku) and (y - y1 >= y0 and y - y1 < y0 + vyskaObrazku):
                # nesmime presunout bod mimo obrazek
                nx, ny = (x - x1, y - y1)
            else:
                # mys je mimo obrazek, ale stale pozouva bod, budeme posouvat bod podel hranice obrazku
                nx, ny = (x - x1, y - y1) # pozici upravime podle toho, ktera strana byla presazena
                if x - x1 < x0:
                    # prekrocena leva hranice obrazku
                    nx = x0
                elif x - x1 > x0 + sirkaObrazku:
                    # prekrocena prava hranice obrazku
                    nx = x0 + sirkaObrazku
                if y - y1 < y0:
                    # prekrocena horni hranice obrazku
                    ny = y0
                elif y - y1 > y0 + vyskaObrazku:
                    # prekrocena dolni hranice obrazku
                    ny = y0 + vyskaObrazku
            # vykreslime bod na upravenou novou pozici
            presouvanyBod.prekresli(okno, (nx, ny))
            pygame.display.flip()
            bodPresunut = True
    elif udalost.type == pygame.KEYDOWN:
        # zmacknuta klavesa
        #print "Key %r" % udalost.unicode # vypise kod klavesy
        if udalost.key == pygame.K_RIGHT:
            # sipka doprava => zobraz dalsi obrazek
            if not seznamSouboru.jeKonec():
                # existuje dalsi obrazek => zobraz ho
                zaznam.nastavBody(body, pomer, x0, y0)
                databaze.uloz()
                (x0, y0, sirkaObrazku, vyskaObrazku, pomer, zaznam) = zobrazDalsiObrazek(seznamSouboru, okno, databaze, body)
        elif udalost.key == pygame.K_LEFT:
            # sipka doleva => zobraz predchozi obrazek
            if not seznamSouboru.jeZacatek():
                # existuje predchozi obrazek => zobraz ho
                zaznam.nastavBody(body, pomer, x0, y0)
                databaze.uloz()
                (x0, y0, sirkaObrazku, vyskaObrazku, pomer, zaznam) = zobrazPredchoziObrazek(seznamSouboru, okno, databaze, body)
        elif udalost.key == pygame.K_ESCAPE:
            # esc => ukonci program
            zaznam.nastavBody(body, pomer, x0, y0)
            databaze.uloz()
            exit()
        else:
            # ostatni klavesy ignorujeme
            pass
    elif udalost.type == pygame.QUIT:
        # ukonceni aplikace krizkem
        zaznam.nastavBody(body, pomer, x0, y0)
        databaze.uloz()
        exit()

