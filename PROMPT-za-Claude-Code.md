# Prompt za Claude Code: Nutribox (landing i stranica sa jelovnikom)

Ceo ovaj fajl je kontekst projekta. Pročitaj ga do kraja pre nego što bilo šta radiš.

## Zadatak

1. Repo je `github.com/floumate-dev/nutribox`, grana `main`. Proveri da li već sadrži commit "Nutribox: prodajna stranica, stranica sa jelovnikom, slike i podaci" i foldere `design/`, `assets/`, `jelovnik/`, `tools/` i `README.md`.
2. Ako sve to postoji, ništa ne menjaj i samo mi potvrdi šta si našao.
3. Ako je repo prazan ili nešto fali, raspakuj `nutribox.zip` u root repoa sa istom strukturom (opisana je ispod), commituj i pushuj na `main`. Ne pravi duplikate fajlova koji već postoje.
4. Posle toga čekaj sledeći zadatak. Najverovatnije će biti pretvaranje obe stranice u kod za Webflow (Embed element).

## O projektu

- **Klijent:** Nutribox (nutribox.rs), vlasnik Vuksan Vasić. Nutribox dostavlja dnevne obroke (doručak, užina, ručak i večera) u Beogradu i Novom Sadu, svakog dana.
- **Šta je urađeno:** redizajn prodajne stranice (landing) od nule, po Figma frame-u "Nutribox Sales Page – Desktop 1440" i odgovorima klijenta. Pored toga napravljena je zasebna stranica sa jelovnikom.
- **Gde je rađeno:** na Claude Design canvasu, https://claude.ai/artifact/7kP1rspX9HXfQTPmHyRwyP (privatan link). Repo je kopija svih fajlova sa canvasa.
- **Produkcija:** sajt ostaje na Webflow-u, a stranice se ubacuju preko Embed (custom code) elementa.
- **Jezik:** sav tekst je na srpskom, latinicom.

## Struktura repoa

| Putanja | Sadržaj |
| --- | --- |
| `design/canvas.json` | Raspored artboarda na canvasu i beleške |
| `design/Main.dc.html` | Ceo landing, jedan kod (sekcije s0 do s16) |
| `design/Desktop2.dc.html` | Prikazuje Main, sekcije 8 do 16 |
| `design/Mobile.dc.html`, `Mobile2.dc.html`, `Mobile3.dc.html` | Main na 390 px, delovi 0 do 5, 6 do 10 i 11 do 16 |
| `design/Jelovnik.dc.html` | Stranica sa jelovnikom (header, završni CTA i footer uvozi iz Main) |
| `design/JelovnikMobile.dc.html` | Jelovnik na 390 px |
| `design/meni/` | Pojedinačne slike jela iz ranije verzije; trenutni dizajn ih ne koristi |
| `assets/<id>.<ext>` | Sve slike koje dizajn koristi. U kodu su referencirane kao `/_blob/<id>`; `assets/index.json` mapira id na fajl i dimenzije |
| `jelovnik/` | Vuksanov paket, druga isporuka (8.11.): `jelovnik.json` (napravljen iz Excela i foldera sa fotografijama), Excel `NUTRIBOX_JELOVNIK_9.11-29.11_MAKROI_2.xlsx`, `PROCITAJ - izmene forme.txt` iz prve isporuke i `slike/` (263 fotografije, 800x1000 WebP) |
| `tools/` | Python skripte kojima su generisani delovi stranica i `measure.js` (Playwright) za merenje visina sekcija |

Landing je podeljen na više artboarda samo zato što canvas prikazuje najviše 8000 px po artboardu. U produkciji je to jedna stranica.

## Kako da čitaš .dc.html fajlove

- Markup je između `<x-dc>` i `</x-dc>`. `<helmet>` sadrži Google Fonts link (Outfit, 300 do 800) i `<style>` (klase, hover i media query-ji).
- `{{ putanja }}` je vrednost iz `renderVals()`. `<sc-for list="{{ x }}" as="y">` je petlja, `<sc-if value="{{ x }}">` je uslov, a `<dc-import name="Main" part-from="0" part-to="0">` ubacuje drugi fajl sa propovima.
- Logika je u `<script type="text/x-dc">`: `class Component extends DCLogic { renderVals() { ... } }`. Stanje se menja sa `this.setState(...)`, a događaji su vezani kao `onClick="{{ f.pick }}"`.
- Main bira koje sekcije prikazuje preko propova `partFrom` i `partTo`. Za produkciju treba prikazati sve od 0 do 16.
- Slike jela su na canvasu sprite slike (više jela u jednoj slici, sa `background-position`), jer pojedinačne slike nisu radile na canvasu. U produkciji koristi pojedinačne fotografije iz `jelovnik/slike/`. Polje `slika` u `jelovnik.json` je putanja do fotografije za svako jelo.
- Prelomne tačke su 960 px (tablet) i 640 px (mobilni).

## Landing: sekcije redom

| Wrapper | Sekcija |
| --- | --- |
| s0 | Top bar ("Dostava u Beogradu i Novom Sadu · Poruči danas → prva dostava već u {dan}") i header (novi SVG logo, telefon 0800 001 007, dugme "Izaberi plan") |
| s1 | Hero: bedž "Beograd i Novi Sad", H1, jedno glavno dugme, 5 avatara i "2.500+ korisnika koji su probali Nutribox". Desno je animacija obroka od dizajnera (opcija I): kesa, ručak, večera, užina i doručak uleću sa desne strane (fadeInRight 1s, kašnjenja 0.3 do 2.3s). `#nbx-hero-food` je kutija u desnoj koloni hero sekcije, proporcije 590:516, vertikalno centrirana u odnosu na tekst; pozicije slika su u % te kutije. Do 900 px kutija ide ispod teksta, na celu širinu (najviše 520 px). Hero sekcija ima `overflow: hidden` |
| s2 | Prepoznaješ li svoj dan? |
| s3 | Tabela poređenja ("Isti problem, četiri rešenja...") |
| s4 | Prazan wrapper |
| s5 | Meni slajder sa filterima (Sve, Balance, Fish, Vegetarijanski, Vegan, Posno, Bez glutena), po 18 pravih jela (na užini piše "+ proteinski šejk" kad paket od 2.000 kcal uključuje šejk); dugmad "Izaberi svoj plan" i "Pogledaj meni za narednu nedelju" (vodi na stranicu sa jelovnikom). Odmah zatim sekcija "Nutribox sistem: tri stvari koje ostali ne rade zajedno." |
| s6 | Ko kuva: Vuksan, Miloš i Amer (portreti, Vuksanov tekst, lime highlight u tekstu; Miloš i Amer imaju ulogu "Šef") |
| s7 | Benefiti |
| s8 | Socijalni dokaz: slajder sa 8 video utisaka i zid sa 33 screenshota poruka (9 sa live sajta, 24 nova od Vuksana) u 3 kolone; na desktopu se prvo vidi 9, ostalo posle dugmeta "Prikaži još 24 utiska"; na mobilnom su svi u redu koji se prevlači |
| s9 | Kako funkcioniše, 4 koraka |
| s10 | Ponuda: izbor paketa i dugme "Nastavi na porudžbinu" |
| s11 | Garancija zadovoljstva za paket od 28 dana (u prvih 7 dana vraćamo novac za preostale 3 nedelje) |
| s12 | Zamerke ("Ono što te verovatno još koči.") |
| s13 | Zašto sada |
| s14 | FAQ, 15 pitanja, tekst od klijenta doslovno |
| s15 | Završni CTA: "Ishrana ti može biti rešena već od prekosutra.", 7 stavki, dugme i telefon |
| s16 | Footer kao na live sajtu (Raiffeisen, kartice, podaci o firmi) i "powered by Floumate", plus sticky CTA na mobilnom |

**Prva dostava je uvek prekosutra.** Dan se računa u JS-u (`dayAcc`, `dayGen`): danas + 2 dana, u akuzativu i genitivu.

**Paketi:**

| Trajanje | Cena po danu | Po obroku | Ukupno | Bedž |
| --- | --- | --- | --- | --- |
| 5 dana | 3.200 RSD | 800 RSD | 16.000 RSD | KRENI POLAKO |
| 7 dana | 3.000 RSD | 750 RSD | 21.000 RSD | |
| 20 dana | 2.950 RSD | ~740 RSD | 59.000 RSD | |
| 28 dana | 2.800 RSD | 700 RSD | 78.400 RSD | NAJISPLATIVIJE, istaknut paket |

## Stranica sa jelovnikom (Jelovnik.dc.html)

- Otvara se na **narednoj nedelji**: to je nedelja koja počinje prvog ponedeljka posle današnjeg dana. Jelovnik pokriva 9. do 29. novembra 2026 (tri nedelje).
- Prikazuje svih 7 dana nedelje. Za svaki dan su tu 4 obroka sa slikom, nazivom, kcal i makroima, plus ukupno za dan. Današnji dan dobija oznaku "DANAS".
- **Izbor menija:** Balance, Fish, Vegetarijanski, Vegan, Bez glutena i Posno. Posno prikazuje svih 18 posnih jela iz celog jelovnika.
- **Izbor paketa:** 1.300, 1.600, 2.000, 2.600 i 3.000 kcal. Ispod piše kom paketu ta veličina odgovara. Vegan ide do 2.600 kcal (XL se veganima ne nudi).
- **Šejk:** na užini piše "+ proteinski šejk" (za Vegan "+ biljni proteinski šejk") kad izabrana veličina uključuje šejk.
- **Izbor nedelje:** tri dugmeta, a naredna nedelja je označena.
- **Ostalo:** gore je link "Nazad na početnu". Na dnu su isti završni CTA i footer kao na landingu.
- **Naslov** prati izbor: "Meni za narednu nedelju od 9. do 15. novembra", "Meni za nedelju od ...", a za Posno "Posna jela od 9. do 29. novembra".

## Podaci jelovnika (jelovnik/jelovnik.json)

- **Obim:** 5 menija × 21 dan × 4 obroka = 420 jela i 263 jedinstvene fotografije (druga isporuka; ista jela, nove fotografije za svih 420 obroka, isto jelo u više menija deli fotografiju).
- **Polja:** `meni`, `datum`, `dan`, `obrok`, `jelo`, `sastojci`, `slika`, `sejk_uz_uzinu` i `makroi`. Makroi su po veličinama XS do XL, sa `kcal`, `p`, `uh` i `m`.
- **Veličine:** XS 1300 je NutriSlim (žena). S 1600 je NutriSlim (muškarac) i NutriBalance (žena). M 2000 je NutriBalance (muškarac) i NutriPump (žena). L 2600 je NutriPump (muškarac). XL 3000 je NutriMax (muškarac). Vegan ima XS, S, M i L (XL se ne nudi veganima).
- **Dnevni zbirovi** na stranici su zbir 4 obroka. Provereno je da se poklapaju sa listom "Zbir po danu" u Excelu (svih 525 kombinacija).
- **Posno** su jela koja u nazivu imaju "Posni" ili "Posna" (pravilo klijenta). Regex je `/posn/i`, pa ulaze i dva veganska jela sa "posnim" sosom.
- **Šejk uz užinu:** makroi užine već uključuju proteinski šejk. Porcije po veličini (XS, S, M, L, XL): Balance i Bez glutena 0, 0, 0, 0, 1; Fish 1, 1,5, 1, 1, 2; Vegetarijanski 0,5, 1, 1, 1,5, 1,5; Vegan 0,5, 1, 1,5, 1,5 (biljni protein i soja mleko). 1 porcija = 50 g proteina + 300 ml mleka. U `jelovnik.json` je to polje `sejk_uz_uzinu`, a u Excelu naziv užine ima dodatak " + proteinski šejk", koji je u json-u skinut.
- **Sastojci** postoje u podacima, ali se ne prikazuju.
- Napomenu "Fotografije su ilustrativne" i izmene forme za poručivanje iz `PROCITAJ` fajla klijent je rekao da ignorišemo.

## Odluke koje važe (ne menjaj bez pitanja)

- Bez nav bara, bez konfiguratora u 3 koraka i bez order bumpa.
- Bez VSL-a, bez brojača i "UŽIVO" oznake, bez Google ocena i bez WhatsApp-a.
- Tabela poređenja je netaknuta.
- Pauza je do 16h dan ranije, promena adrese do 6h. Pauza ide iz aplikacije.
- Garancija važi samo za paket od 28 dana.
- **Vreme dostave se nigde ne pominje**: ni "do 9:30", ni jutarnja ili večernja dostava, jer Vuksan razmišlja o uvođenju večernje dostave. Piše samo "svakog dana" i "prva dostava već prekosutra".
- FAQ je tekst klijenta doslovno, osim što je iz odgovora "Kada stiže prva dostava?" izbačena rečenica o terminima dostave. Poznate nedoslednosti (cene 17.400 i 22.400 u FAQ-u naspram 16.000 i 21.000 u paketima, pauza preko podrške 24h naspram 16h iz aplikacije, večernja dostava, posni meni) klijent je rekao da ostanu.
- Ikonice su inline SVG u brendu, nikad emoji.

## Linkovi

- Sva dugmad "Izaberi plan", "Izaberi svoj plan" i "Nastavi na porudžbinu" vode na `https://www.nutribox.rs/order-form`.
- FAQ, besplatan poziv za porodice: `https://app.iclosed.io/e/nutribox/besplatan-poziv-za-porodice`.
- FAQ, besplatan poziv za firme: `https://app.iclosed.io/e/nutribox/besplatan-poziv-za-firme`.
- "powered by Floumate" vodi na `https://www.floumate.com?source=nutribox`.
- "Pogledaj meni za narednu nedelju" na canvasu vodi na `Jelovnik.dc.html`. Produkcijski URL još nije poznat (npr. `nutribox.rs/jelovnik`).
- Telefon je `tel:0800001007`.

## Pravila za tekst i dizajn (obavezno)

- **Nikad em dash (duga crta)**, ni u tekstu, ni u kodu, ni u komentarima.
- **Nikad jedna reč sama u poslednjem redu** bilo kog bloka teksta. Spreči to dizajnom: `&nbsp;` između poslednje dve reči, `text-wrap: pretty` za tekst i `text-wrap: balance` za naslove i centrirane pasuse. Za tekst iz JS-a koristi helper koji poslednji razmak menja sa ` `.
- **Font i boje:**
  - Font je Outfit.
  - Tamnozelena #123c32 je za tekst i glavna dugmad.
  - Zelena #5e8f3d je za drugi deo naslova, a tamnija zelena #4d7a31 za sitan tekst.
  - Lime #accb7d je za akcente i highlight.
  - Svetle pozadine su #f0f6ec i #f6f8f3, osnovni tekst je #3d4a41, a ivice #e3e8e2.
- Touch target je najmanje 44 px. Koristi prave `<button>` i `<a href>` elemente.

## Otvoreno (čeka klijenta)

1. Produkcijski URL stranice sa jelovnikom.
