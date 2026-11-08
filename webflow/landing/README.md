# Landing za Webflow

Kod za ubacivanje prodajne stranice u Webflow. Sve fajlove pravi `tools/build_webflow.py` iz `design/Main.dc.html`, pa ih ne menjaj ručno.

| Fajl | Gde ide u Webflow-u |
| --- | --- |
| `head.html` | Page settings > Custom code > **Inside `<head>` tag** |
| `embed-01.html`, `embed-02.html`, `embed-03.html` | Tri **Embed** elementa, redom, direktno u Body |
| `footer.html` | Page settings > Custom code > **Before `</body>` tag** |
| `landing.css`, `landing.js` | Ne kopiraju se. `head.html` i `footer.html` ih učitavaju preko jsDelivr-a |

## Postavljanje

1. U Webflow-u napravi novu praznu stranicu, bez navigacije i footera sajta. Header i footer su već u kodu.
2. U Navigator prevuci tri **Embed** elementa direktno u **Body**, jedan ispod drugog. Ne stavljaj ih u Section, Container ili Div Block, jer Webflow Container ima max-width i suziće stranicu.
3. U prvi Embed nalepi ceo sadržaj fajla `embed-01.html`, u drugi `embed-02.html`, a u treći `embed-03.html`. Svaki fajl je ispod Webflow-ovog limita od 50.000 karaktera.
4. Page settings > Custom code: sadržaj `head.html` ide u polje *Inside `<head>` tag*, a `footer.html` u polje *Before `</body>` tag*.
5. Publish, pa proveri stranicu na objavljenom URL-u.

U Designer-u se stranica vidi delimično stilizovana, jer Webflow ne pokreće custom code u Designer-u. Prava slika je tek na objavljenoj stranici ili u Preview-u na staging domenu.

## Kako radi

- HTML u Embed elementima je unapred renderovan. Tekst je u samom HTML-u stranice, pa ga Google vidi bez JavaScript-a, a stranica se prikazuje odmah.
- `landing.js` posle učitavanja preuzima taj HTML i dodaje interakcije: filtere u meniju, izbor paketa, "Prikaži još" na zidu sa porukama, FAQ i datum prve dostave u top baru. Datum se računa u browseru, pa je uvek tačan.
- Sve klase iz dizajna imaju prefiks `nbx-`, da se ne sudaraju sa klasama sajta (sajt npr. već ima `.slider`). `landing.css` vraća podrazumevane stilove browsera unutar stranice, jer Webflow menja h1-h6, p, img i box-sizing.
- Slike, `landing.css` i `landing.js` se serviraju preko jsDelivr CDN-a iz ovog repoa, zaključani na commit. Kasnija izmena u repou ne menja objavljenu stranicu dok se linkovi ne zamene.

## Izmena stranice

1. Izmeni `design/Main.dc.html` (ili ga zameni exportom sa canvasa).
2. `python3 tools/build_webflow.py build`, pa commit i push.
3. `python3 tools/build_webflow.py snippets <sha tog commita>`, pa commit i push.
4. U Webflow-u zameni sadržaj sva tri Embed-a i oba polja za custom code novim fajlovima, pa Publish. Ako se promenio broj `embed-*.html` fajlova, dodaj ili ukloni Embed elemente.

## Otvoreno

- Dugme "Pogledaj meni za narednu nedelju" vodi na `/jelovnik`. Kad bude poznat pravi URL stranice sa jelovnikom, promeni `JELOVNIK_URL` u `tools/build_webflow.py` i uradi build.
- Dugmad za puštanje video utisaka za sada nemaju akciju, jer u dizajnu nema linkova do videa.
