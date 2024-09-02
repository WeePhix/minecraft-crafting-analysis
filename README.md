# Analiza receptov za izdelavo predmetov v računalniški igri Minecraft

## Opis

Program iz spleta naloži HTML iz glavne spletne strani za računalniško igro Minecraft in iz nje izlušči vse možne recepte za izdelavo predmetov in jih shrani v CSV tabelo. Te nato analizira (za vsak predmet poišče, kaj vse se da iz njega narediti, kaj vse je potrebno, za izdelavo tega predmeta, in koliko vsakega materiala je potrebnega, ter prešteje, koliko operacij "crafting"-a moramo opraviti, da iz primarnih materialov dobimo ta predmet). Vse to nato shrani v novo CSV tabelo.

## Delovanje

Najprej program `main.py` iz spleta naloži HTML datoteko. To z regularnimi izrazi razdeli na različne razdelke in nato vsak razdelek na različne predmete. Podatke o predmetih sproti shranjuje v objekte in jih nazadnje vse zapiše v datoteko `data.csv`.

Program `analiza.ipynb` nato iz te datoteke prebere vse podatke o vsakem predmetu, jih spet shrani v objekte in jih analizira: Definira primarne in končne predmete (primarni so takšni, ki se jih ne da izdelati, končni so pa tisti, iz katerih ni mogoče izdelati ničesar drugega), za vsak predmet poišče vse potrebne primarne materiale in vse predmete, ki jih je moč narediti iz njega. Sproti tudi preveri, kaj je najdaljša veriga receptov za vsak predmet, od primarnih materialov do izbranega predmeta. Vse te podatke tudi predstavi v grafih in tabelah, ter jih shrani v tabelo `extracted.csv`.

## Uporaba

Za uporabo projekta morate imeti naložene naslednje knjižnice:
- selenium
- pandas
- matplotlib
Naložite jih lahko tako, da v terminal vtipkate `pip install <knjižnica>`, kjer `<knjižnica>` nadomestite z manjkajočo knjižnico

Poleg tega, je bil program napisan v verziji 3.12.5 programskega jezika Python, zato pri poskusu zagona programa s starejšo različico morda pride do težav.

V `main.py` je proti začetku programa spremenljivka `download_from_web` nastavljena na `True`. Če vam program vrne napako, povezano s knjižnico selenium, spremenite to spremenljivko na `False` in se prepričajte, da imate naloženih vseh 11 datotek s končnico `.txt` v podmapi `data`.
V `analiza.ipynb` boste naleteli na `if` stavek, katerega argument bo `False`. Če želite videti vse nabrane podatke o vsakem predmetu, ta argument nastavite na `True`. To je tako nastavljeno, saj je izpis podatkov o vseh predmetih zelo dolg.