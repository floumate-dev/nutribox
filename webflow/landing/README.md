# Landing za Webflow (SR, EN, RU)

Kod za ubacivanje prodajne stranice u Webflow, na srpskom, engleskom i ruskom. Sve fajlove pravi `tools/build_webflow.py` iz `design/Main.dc.html` (sr), `design/Main.en.dc.html` (en) i `design/Main.ru.dc.html` (ru). Ne menjaj ih ručno.

| Fajl | Gde ide u Webflow-u |
| --- | --- |
| `head.html` | Page settings > Custom code > **Inside `<head>` tag** (isto za sve jezike) |
| `footer.html` | Page settings > Custom code > **Before `</body>` tag** (isto za sve jezike, sam učitava JS za jezik stranice) |
| `embed-sr-01.html` … `embed-sr-03.html` | tri **Embed** elementa za srpski |
| `embed-en-01.html` … | Embed elementi za engleski |
| `embed-ru-01.html` … | Embed elementi za ruski |
| `landing.css`, `landing.sr.js`, `landing.en.js`, `landing.ru.js` | Ne kopiraju se. Učitavaju se preko jsDelivr-a |

## Postavljanje

1. Stranica treba da bude prazna, bez navigacije i footera sajta, jer su header i footer već u kodu.
2. U Navigator prevuci Embed elemente **direktno u Body**, redom: prvo srpski (`embed-sr-01`, `-02`, `-03`), pa engleski, pa ruski. Ne stavljaj ih u Section, Container ili Div Block.
3. U svaki Embed nalepi ceo sadržaj odgovarajućeg fajla. Svaki fajl je ispod Webflow-ovog limita od 50.000 karaktera.
4. **Vidljivost po jeziku.** Webflow ne prevodi sadržaj Embed elemenata, pa svaki jezik ima svoje. U Designer-u prebaci na lokal English, selektuj srpske i ruske Embed-e i u Settings panelu isključi im vidljivost (Element visibility: Hidden). Na lokalu Russian sakrij srpske i engleske, a na primarnom (srpskom) sakrij engleske i ruske. Svaki jezik tako u HTML-u ima samo svoj tekst, što je važno za Google.
5. Page settings > Custom code: `head.html` u *Inside `<head>` tag*, `footer.html` u *Before `</body>` tag*. Isti kod važi za sve jezike, ne treba ga menjati po lokalu.
6. Publish, pa proveri `/stranica`, `/en/stranica` i `/ru/stranica`.

Ako vidljivost iz koraka 4 nije podešena, stranica i dalje radi: CSS sakriva Embed-e drugih jezika. Ali tada se tekst svih jezika nalazi u HTML-u svake verzije.

U Designer-u se stranica vidi delimično stilizovana, jer Webflow ne pokreće custom code u Designer-u. Pravi izgled je tek na objavljenoj stranici.

## Kako radi

- HTML u Embed elementima je unapred renderovan. Tekst je u samom HTML-u stranice, pa ga Google vidi bez JavaScript-a, a stranica se prikazuje odmah.
- `footer.html` čita `lang` atribut stranice (Webflow ga postavlja po lokalu: `sr`, `en`, `ru`) i učitava `landing.<lang>.js`. Taj fajl preuzima HTML tog jezika i dodaje interakcije: filtere u meniju, izbor paketa, "Prikaži još", FAQ i datum prve dostave.
- **Switcher jezika** (SR / EN / RU) pravi skripta iz custom code-a celog sajta. Na ovoj stranici `landing.js` premešta njegovu kopiju u header (pored telefona), a na telefonu i tabletu pored bedža "Beograd i Novi Sad" u hero sekciji. Plutajući switcher iz gornjeg desnog ugla se sakriva.
- **Linkovi unutar stranice** (npr. "Pogledaj po čemu je Nutribox drugačiji") skroluju nativno i staju ispod sticky top bara. Webflow-ov skrol se ovde ne koristi, jer se sudarao sa CSS `scroll-behavior: smooth` i kasnio.
- Sve klase iz dizajna imaju prefiks `nbx-`, da se ne sudaraju sa klasama sajta (sajt npr. već ima `.slider`). `landing.css` vraća podrazumevane stilove browsera unutar stranice, jer Webflow menja h1-h6, p, img i box-sizing.
- Font: Outfit nema ćirilicu, pa se ruski tekst prikazuje fontom Onest (sličan, geometrijski). Browser ga preuzima samo kad stranica ima ćirilicu.
- Slike, CSS i JS se serviraju preko jsDelivr CDN-a iz ovog repoa, zaključani na commit. Kasnija izmena u repou ne menja objavljenu stranicu dok se linkovi ne zamene.

## Izmena stranice

1. Izmeni `design/Main.dc.html` i istu izmenu prenesi u `Main.en.dc.html` i `Main.ru.dc.html`. Posle prevoda pokreni `python3 tools/check_translation.py design/Main.en.dc.html` (i za `ru`), koji proverava da se prevod razlikuje samo u tekstu.
2. `python3 tools/build_webflow.py build landing`, pa commit i push.
3. `python3 tools/build_webflow.py snippets <sha tog commita> landing`, pa commit i push.
4. U Webflow-u zameni sadržaj Embed-a i oba polja za custom code novim fajlovima, pa Publish. Ako se promenio broj `embed-*.html` fajlova, dodaj ili ukloni Embed elemente.

## Otvoreno

- Dugme "Pogledaj meni za narednu nedelju" vodi na `/jelovnik` (`/en/jelovnik`, `/ru/jelovnik`). Kad bude poznat pravi URL, promeni `JELOVNIK_URL` u `tools/build_webflow.py` i uradi build.
- Stranica sa jelovnikom je u `webflow/jelovnik/` (svoje uputstvo).
