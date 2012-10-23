Návod k použití
===============

body.py
-------

Slouží k naklikání okrajových bodů kořene.
Spuští se příkazem: 
  `python body.py slozka`
Program postupně zobrazí všechny obrázky ve složce `slozka` a naklikané body 
uloží do souboru `slozka.csv`. Pokud tento soubor neexistuje, tak ho vyrobí.


barvy.py
--------

Slouží k obtažení kořenů jednolitými barvami, aby pak kořeny mohly být 
lépe zpracovány ostatními programy.
Spouští se příkazem:
  `python barvy.py slozka`


analyzuj-pozadi.py
------------------

Slouží k převedení obrázku na černobílý. Pozadí je černé, kořen bílý.
Spouští se příkazem:
  `python analyzuj-pozadi.py slozka1 slozka2`
Obrázky ze slozky `slozka1` budou převedeny na černobílé a budou uloženy
do složky `slozka2`. Obě složky mohou být stejné. Obrázky budou uloženy
s koncovkou `.root.png`.


analyzuj-kostru.py
------------------

Slouží k výpočtu různých parametrů kostry. Kostra musí být zadaná ve formě
černobílého obrázku, kde pozadí je černé a kostra je bílá. Obrázky kostry
musí mít koncovku `.skel.png`. 
Spouští se příkazem:
  `python analyzuj-kostru.py slozka1 slozka2 slozka3 soubor.csv`
Kostry ze složky `slozka2` budou analyzovány. Ve složce `slozka1` jsou originální
obrázky, ze kterých byly kostry vypočteny. Ty slouží k analýze barev. 
Do složky `slozka3` budou uloženy obarvené kostry. Do souboru `soubor` 
budou uloženy vypočtené statistiky ve formátu csv. Pokud 
tento soubor již existuje, bude přepsán.
