# Jelovnik za Webflow (SR, EN, RU)

Stranica sa jelovnikom za narednu nedelju, na srpskom, engleskom i ruskom. Sve fajlove pravi `tools/build_webflow.py` iz `design/Jelovnik.dc.html` (sr), `design/Jelovnik.en.dc.html` (en) i `design/Jelovnik.ru.dc.html` (ru). Header, završni CTA i footer su delovi landinga (`design/Main*.dc.html`). Ne menjaj fajlove ručno.

| Fajl | Gde ide u Webflow-u |
| --- | --- |
| `head.html` | Page settings > Custom code > **Inside `<head>` tag** (isto za sve jezike) |
| `footer.html` | Page settings > Custom code > **Before `</body>` tag** (isto za sve jezike, sam učitava JS za jezik stranice) |
| `embed-sr-NN.html` | **Embed** elementi za srpski |
| `embed-en-NN.html` | Embed elementi za engleski |
| `embed-ru-NN.html` | Embed elementi za ruski |
| `jelovnik.css`, `jelovnik.sr.js`, `jelovnik.en.js`, `jelovnik.ru.js` | Ne kopiraju se. Učitavaju se preko jsDelivr-a |

## Postavljanje

1. Napravi novu praznu stranicu sa slug-om **`jelovnik`**, bez navigacije i footera sajta. Na landingu dugme "Pogledaj meni za narednu nedelju" vodi na `/jelovnik` (`/en/jelovnik`, `/ru/jelovnik`). Ako izabereš drugi slug, javi da se promeni link.
2. U Navigator prevuci Embed elemente **direktno u Body**, redom: prvo srpske, pa engleske, pa ruske. Ne stavljaj ih u Section, Container ili Div Block.
3. U svaki Embed nalepi ceo sadržaj odgovarajućeg fajla. Svaki je ispod Webflow-ovog limita od 50.000 karaktera.
4. **Vidljivost po jeziku**, isto kao na landingu: na lokalu English sakrij srpske i ruske Embed-e (Element visibility: Hidden), na Russian srpske i engleske, a na primarnom (srpskom) engleske i ruske.
5. Page settings > Custom code: `head.html` u *Inside `<head>` tag*, `footer.html` u *Before `</body>` tag*.
6. Publish, pa proveri `/jelovnik`, `/en/jelovnik` i `/ru/jelovnik`.

## Kako radi

- HTML u Embed elementima je unapred renderovan za podrazumevani izbor (Balance, 2.000 kcal, naredna nedelja), pa je tekst odmah na stranici i vidljiv Google-u. `jelovnik.<lang>.js` posle učitavanja preuzima stranicu i dodaje izbor menija, paketa i nedelje. "Naredna nedelja" i oznaka "danas" računaju se po datumu u browseru.
- Slike jela su sprite slike (sva jela jedne nedelje jednog menija u jednoj slici), pa se pri promeni nedelje ili menija učitava samo jedna slika.
- Link "Nazad na početnu" vodi na `/` (`/en`, `/ru`). Kad landing dobije svoj konačni URL, promeni `LANDING_URL` u `tools/build_webflow.py` i uradi build.
- Switcher jezika, klase sa prefiksom `nbx-`, Webflow reset i font Onest za ćirilicu rade isto kao na landingu (vidi `webflow/landing/README.md`).

## Novi jelovnik

Jelovnik pokriva 9.11. do 29.11.2026. Za sledeći period treba novi `design/Jelovnik.dc.html` sa canvasa (podaci i sprite slike), prevod jela u `Jelovnik.en.dc.html` i `Jelovnik.ru.dc.html` (`tools/check_translation.py` proverava da se razlikuju samo u tekstu), pa `python3 tools/build_webflow.py build jelovnik` i `snippets <sha> jelovnik`, i zamena Embed-a i custom code-a u Webflow-u.
