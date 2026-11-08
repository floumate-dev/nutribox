import sys

p = sys.argv[1]
s = open(p, encoding="utf-8").read()

start = "    const P = '[Odgovor stiže od Vuksana]';\n"
end = "        q: nb(q), a: nb(a), open, closed: !open,\n"
assert s.count(start) == 1 and s.count(end) == 1
a = s.index(start)
b = s.index(end) + len(end)

new = r"""    // FAQ od Vuksana (7. 11. 2026); treca kolona je opcioni link ispod odgovora
    const faqDefs = [
      ['Koji paket da izaberem?', 'Paket biraš prema svom cilju. NutriSlim (1300 kcal za žene, 1600 kcal za muškarce) je za mršavljenje, NutriBalance (1600/2000 kcal) za održavanje težine, a NutriPump (2000/2600 kcal) za aktivne i izgradnju mišića. NutriMax (3000 kcal) je samo za veoma aktivne muškarce. Kalorije su tačne, dok makronutrijenti mogu blago da variraju u zavisnosti od obroka. Ako nisi siguran, pozovi korisničku podršku na 0800 001 007 i pomoći ćemo ti da izabereš.'],
      ['Gde dostavljate?', 'Dostavljamo u Beogradu i Novom Sadu. U Beogradu zasad ne dostavljamo u Železnik, Borču, Kaluđericu i prigradske opštine. Za proveru tvoje adrese pozovi korisničku podršku na 0800 001 007.'],
      ['Kada stiže prva dostava?', 'Prva dostava stiže najranije prekosutra od dana porudžbine. Svi obroci za taj dan stižu u jednoj isporuci na tvoju adresu, a možeš da biraš jutarnju dostavu od 6:30 do 9:30 ili večernju od 19h do 22h.'],
      ['Mogu li prvo da probam?', 'Možeš. Kreni sa planom od 5 dana, koji je samo za radne dane, ili sa planom od 7 dana. Cena za XS–M veličine je 17.400 RSD za 5 dana i 22.400 RSD za 7 dana. Ako ti se dopadne, doplatom razlike prelaziš na plan od 20, odnosno 28 dana i dobijaš bonus dane gratis.'],
      ['Šta ako mi Nutribox ne odgovara?', 'Uz plan od 28 dana imaš garanciju zadovoljstva. Ako ti u prvih 7 dana nešto ne odgovara, javi se korisničkoj podršci na 0800 001 007 i prvo ćemo pokušati da to ispravimo. Ako ni tada nisi zadovoljan i imaš opravdan razlog, vraćamo ti novac za preostale 3 nedelje. Sve uslove pročitaj u pravilima o povraćaju sredstava.', ['Pravila o povraćaju sredstava', 'https://www.nutribox.rs/politika-povracaja-sredstava']],
      ['Šta mogu da izbacim iz menija?', 'To zavisi od menija koji izabereš. U Balance meniju možeš da izbaciš najviše dve stavke od sledećih: gluten, riba, svinjetina i laktoza, s tim što laktoza i gluten ne mogu zajedno. U Fish meniju možeš da izbaciš gluten ili laktozu, ali ne oba, u Vegetarijanskom samo gluten, a Vegan meni nema izmena. Umesto obroka sa onim što si izbacio, dobijaš odgovarajuću zamenu. Ostale namirnice ne možemo da izbacujemo pojedinačno.'],
      ['Da li imate posni meni ili meni bez glutena?', 'Imamo oba. Posni meni dolazi u tri veličine, 1300, 1600 i 2200 kcal, i može da sadrži ribu. Gluten možeš da izbaciš iz Balance, Fish i Vegetarijanskog menija, a umesto obroka sa glutenom dobijaš odgovarajuću zamenu. Obroci se pripremaju u kuhinji u kojoj se koristi i gluten, pa ako imaš celijakiju, prvo pozovi korisničku podršku na 0800 001 007.'],
      ['Da li hrana mora da se podgreje?', 'Hrana stiže hladna i odmah je čuvaj u frižideru. Većinu obroka možeš da podgreješ u mikrotalasnoj, rerni ili air fryeru, a neki se jedu hladni. Kako da pripremiš obroke, pogledaj u kratkim video lekcijama na našoj platformi.'],
      ['Mogu li da pauziram ili promenim adresu?', 'Naravno, samo se javi korisničkoj podršci na 0800 001 007. Ako pauzu najaviš najmanje 24 sata pre dostave, taj dan ostaje sačuvan. Ako se javiš kasnije, na primer noću za sutra ujutru, obrok je već spreman, pa se dan računa kao iskorišćen.'],
      ['Kako se plaća?', 'Možeš da platiš karticom online pri poručivanju, pouzećem, gotovinom vozaču prilikom prve dostave, ili preko fakture.'],
      ['Da li možemo da poručimo u dvoje?', 'Možete. Poruči svoj plan, a partnera dodajemo na pozivu sa korisničkom podrškom posle porudžbine. Partnerov plan je jeftiniji: 8.400 RSD uz plan od 28 dana, 6.000 RSD uz 20 dana, 2.100 RSD uz 7 dana i 1.500 RSD uz 5 dana. Svako bira svoj meni i veličinu paketa, a oba paketa stižu na istu adresu.'],
      ['Imam insulinsku rezistenciju. Da li je ovo za mene?', 'Može da bude dobar izbor. Naši obroci su zdravi, bogati proteinima, zdravim mastima i vlaknima, a za svaki paket su unapred određene kalorije i makronutrijenti. NutriSlim ima najmanje ugljenih hidrata, ali obroci nisu pravljeni posebno za insulinsku rezistenciju i ne prilagođavamo ih pojedinačno. Zato izbor paketa proveri sa svojim lekarom ili nutricionistom, a za detalje o obrocima pozovi korisničku podršku na 0800 001 007.'],
      ['Da li postoje dodaci?', 'Postoje. Uz plan možeš da dodaš kolače, proteinske šejkove i druge dodatke za 450 RSD po komadu, kao i dodatnih 30 g proteina uz doručak, ručak ili večeru za 440 RSD. Pri poručivanju možeš da dodaš i dnevnu supu ili potaž i dodatnu užinu, a cena zavisi od dužine plana.'],
      ['Da li postoji ponuda na nekoliko meseci?', 'Postoji. Možeš da potpišeš ugovor na 3, 6 ili 12 meseci i plaćaš mesec za mesec. Ugovor na 3 meseca ti otključava dodatne užine, a uz ugovor na 6 meseci paket traje 30 dana umesto 28. Ugovor na 12 meseci otključava sve bonuse. Ako uplatiš više meseci unapred, popust i dodatne bonuse dogovaramo na pozivu. Za više informacija pozovi korisničku podršku na 0800 001 007.'],
      ['Hrana za firmu?', 'Imamo posebnu ponudu za firme. Zaposleni kroz Nutribox aplikaciju biraju ručak i užinu iz baze od preko 20 jela dnevno, a dostava stiže na adresu firme. Paket košta 1.700 RSD po zaposlenom dnevno. Troškove može da pokrije firma, delom firma i zaposleni, ili sami zaposleni, pa to dogovaramo ugovorom. Zakaži razgovor i pripremićemo ponudu za tvoju firmu.', ['Zakaži razgovor', '#b2b']]
    ];
    const faqs = faqDefs.map(([q, a, link], i) => {
      const open = i === openFaq;
      return {
        num: String(i + 1).padStart(2, '0'),
        q: nb(q), a: nb(a), open, closed: !open,
        hasLink: open && !!link,
        linkLabel: link ? link[0] : '',
        linkHref: link ? link[1] : '#',
"""
s = s[:a] + new + s[b:]

# link under the open answer
old_t = '<p style="margin: 0; padding: 0 22px 22px 66px; font-size: 16px; line-height: 1.6; color: #e6eee3">{{ q.a }}</p>'
assert s.count(old_t) == 1
new_t = old_t + '''
<sc-if value="{{ q.hasLink }}" hint-placeholder-val="{{ false }}">
<div style="padding: 0 22px 22px 66px; margin-top: -8px">
<a href="{{ q.linkHref }}" style="display: inline-flex; align-items: center; gap: 8px; min-height: 44px; font-size: 16px; font-weight: 700; color: #accb7d">{{ q.linkLabel }}
<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"></path><path d="M13 6l6 6-6 6"></path></svg>
</a>
</div>
</sc-if>'''
s = s.replace(old_t, new_t)
s = s.replace('<sc-for list="{{ faqs }}" as="q" hint-placeholder-count="13">', '<sc-for list="{{ faqs }}" as="q" hint-placeholder-count="15">')
open(p, "w", encoding="utf-8").write(s)
print("ok")
