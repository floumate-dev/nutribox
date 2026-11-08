# Nutribox: nova prodajna stranica i jelovnik

Izvorni fajlovi redizajna prodajne stranice za nutribox.rs (klijent: Vuksan Vasić) i zasebne stranice sa jelovnikom. Dizajn je rađen na Claude Design canvasu; ovaj repo je kopija svih fajlova sa canvasa, slika i podataka.

## Struktura

| Folder | Šta je unutra |
| --- | --- |
| `design/` | Fajlovi sa canvasa: `canvas.json` (raspored artboarda i beleške) i `.dc.html` artboardi |
| `assets/` | Sve slike koje dizajn koristi. U kodu su referencirane kao `/_blob/<id>`, ovde su `assets/<id>.<ext>`. `index.json` mapira id na fajl i dimenzije |
| `jelovnik/` | Vuksanov paket: `jelovnik.json`, Excel sa slikama i makroima, uputstvo za developere i `slike/` (304 fotografije, 800x1000 WebP) |
| `tools/` | Python skripte kojima su generisani delovi stranice (jelovnik, sprite slike, FAQ, footer) i `measure.js` za merenje visina sekcija |

## Artboardi u `design/`

| Fajl | Šta je |
| --- | --- |
| `Main.dc.html` | Cela prodajna stranica (jedan kod). Prikazuje deo stranice preko propova `partFrom` i `partTo` (sekcije 0 do 16) |
| `Desktop2.dc.html` | Drugi deo desktop verzije (sekcije 8 do 16) |
| `Mobile.dc.html`, `Mobile2.dc.html`, `Mobile3.dc.html` | Mobilna verzija u tri dela (0 do 5, 6 do 10, 11 do 16) |
| `Jelovnik.dc.html` | Stranica sa jelovnikom za narednu nedelju: izbor menija, veličine paketa i nedelje |
| `JelovnikMobile.dc.html` | Mobilni prikaz stranice sa jelovnikom |

Stranica je podeljena na delove samo zato što canvas prikazuje najviše 8000 px po artboardu.

## Napomene

- Slike jela na stranicama su sprite slike (više jela u jednoj slici). Jelovnik koristi jednu sliku po meniju i nedelji (4 obroka x 7 dana), prodajna stranica jednu po filteru.
- `design/meni/` su pojedinačne slike jela iz ranije verzije; trenutni dizajn ih ne koristi.
- Hero vizual je privremeno placeholder dok Vuksan ne odluči šta ide tu.
- Za Webflow fali URL stranice sa jelovnikom (npr. nutribox.rs/jelovnik), za dugme "Pogledaj meni za narednu nedelju".
