Návod k použití
===============

body.py
-------

Slouží k naklikání okrajových bodů kořene.
Spuští se příkazem: 
  `python body.py slozka`
Program postupně zobrazí všechny obrázky ve složce `slozka` a naklikané body 
uloží do souboru `slozka.csv`. Pokud tento soubor neexistuje, tak ho vyrobí.


colors.py
--------

Slouží k obtažení kořenů jednolitými barvami, aby pak kořeny mohly být 
lépe zpracovány ostatními programy.
Spouští se příkazem:
  `python colors.py slozka`


analyze-background.py
------------------

Slouží k převedení obrázku na černobílý. Pozadí je černé, kořen bílý.
Spouští se příkazem:
  `python analyze-background.py slozka1 slozka2`
Obrázky ze slozky `slozka1` budou převedeny na černobílé a budou uloženy
do složky `slozka2`. Obě složky mohou být stejné. Obrázky budou uloženy
s koncovkou `.root.png`.


skeleton.ijm
----------

Toto je makro do programu fiji. Slouží k získání kostry z černobílého
obrázku. Spouští se příkazem:
  `fiji -batch skeleton.ijm slozka1:slozka2`
Pozor, jména složek jsou od sebe odděleny dvojtečkou.
Ve složce `slozka1` musí být černobílé obrázky kořenů s koncovkami
`.root.png`. Všechny tyto obrázky budou analyzovány a uloženy do složky
`slozka2` s koncovkami `.skel.png`. 


analyze-skeleton.py
------------------

Slouží k výpočtu různých parametrů kostry. Kostra musí být zadaná ve formě
černobílého obrázku, kde pozadí je černé a kostra je bílá. Obrázky kostry
musí mít koncovku `.skel.png`. 
Spouští se příkazem:
  `python analyze-skeleton.py slozka1 slozka2 slozka3 soubor.csv`

Ve složce `slozka1` jsou originální obrázky, ze kterých byly kostry 
vypočteny. Ty slouží k analýze barev. Ve složce `slozka2` jsou černobílé
kostry, které budou analyzovány. Do složky `slozka3` budou uloženy 
obarvené kostry. Do souboru `soubor` budou uloženy vypočtené statistiky 
ve formátu csv. Pokud již tento soubor již existuje, bude přepsán.


analyze.bash
-------------

Skript, který spustí postupně `analyze-background.py`, `skeleton.ijm` 
a `analyze-skeleton.py`. Spouští se příkazem:
  `bash analyze.bash slozka zkratka`
nebo:
  `bash analyze.bash slozka zkratka cislo`
Složka `slozka` musí mít několik podsložek, které všechny začínají řetězcem
`zkratka`. Tyto složky jsou:
 - prekreslene: Zde musí být obrázky kořenů.
 - cernobile: Zde budou vygenerovány černobílé obrázky kořenů.
 - kostry: Zde budou vygenerovány černobílé obrázky koster.
 - barevnekostry: Zde budou vygenerovány barevné obrázky koster a csv soubor
     s výsledky.
Parametr `cislo` je volitelný. Pokud není uveden, jsou spuštěny všechny tři 
skripty. Pokud je uveden, musí to být číslo 1, 2 nebo 3 a bude spuštěn pouze
první, druhý nebo třetí skript.

