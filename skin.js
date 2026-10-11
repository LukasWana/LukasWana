/* Vzhled: tlačítko s panelem „Vzhled a motivy“ (docs/plans/2026-10-11-skiny-design.md).
   Barvy jsou jen ve skiny.css. Tady je seznam voleb a stavba panelu; náhledy v panelu nesou data-skin /
   data-akcent / data-pozadi a data-rezim, takže je obarví tytéž bloky CSS jako stránku.
   Atributy na <html> nastavuje už skript v <head> před vykreslením; tenhle soubor je udržuje a ukládá. */
(function () {
  'use strict';

  var SKINY = [
    { id: 'inkoust', nazev: 'Inkoust' },
    { id: 'teple', nazev: 'Veselé' },     // dřív „Teplé světlo“; id zůstalo kvůli uloženým volbám
    { id: 'hluboka', nazev: 'Voda' },     // dřív „Hluboká práce“
    { id: 'priroda', nazev: 'Příroda' }
  ];
  var AKCENTY = [
    { id: 'fialova', nazev: 'Fialová' },
    { id: 'purpur', nazev: 'Purpurová' },
    { id: 'malina', nazev: 'Malinová' },
    { id: 'oranzova', nazev: 'Oranžová' },
    { id: 'zelena', nazev: 'Zelená' },
    { id: 'tyrkys', nazev: 'Tyrkysová' },
    { id: 'modra', nazev: 'Modrá' }
  ];
  var POZADI = [
    { id: 'papir', nazev: 'Papír' },
    { id: 'mrizka', nazev: 'Mřížka' },
    { id: 'tecky', nazev: 'Tečky' }
  ];
  var REZIMY = [
    { id: 'svetly', nazev: 'Světlý', ikona: '<circle cx="8" cy="8" r="3" fill="currentColor"/><path d="M8 1v2M8 13v2M1 8h2M13 8h2M3 3l1.4 1.4M11.6 11.6L13 13M3 13l1.4-1.4M11.6 4.4L13 3" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>' },
    { id: 'tmavy', nazev: 'Tmavý', ikona: '<path d="M13.5 10A6 6 0 0 1 6 2.5a6 6 0 1 0 7.5 7.5z" fill="currentColor"/>' },
    { id: 'system', nazev: 'Systém', ikona: '<circle cx="8" cy="8" r="6.3" fill="none" stroke="currentColor" stroke-width="1.4"/><path d="M8 1.7a6.3 6.3 0 0 1 0 12.6z" fill="currentColor"/>' }
  ];

  // Uložená hodnota platí jen z daného seznamu; jinak výchozí (první skin, bez akcentu a vzoru, režim podle systému)
  function platne(seznam, id, vychozi) {
    for (var i = 0; i < seznam.length; i++) {
      if (seznam[i].id === id) return id;
    }
    return vychozi;
  }

  function stav(ulozene) {
    return {
      skin: platne(SKINY, ulozene.skin, SKINY[0].id),
      volba: platne(REZIMY, ulozene.rezim, 'system'),
      akcent: platne(AKCENTY, ulozene.akcent, ''),
      pozadi: platne(POZADI, ulozene.pozadi, '')
    };
  }

  // Volba režimu (svetly / tmavy / system) → skutečný režim stránky (svetly / tmavy)
  function rezim(volba, systemTmavy) {
    if (volba === 'svetly' || volba === 'tmavy') return volba;
    return systemTmavy ? 'tmavy' : 'svetly';
  }

  function moznost(skupina, id, s, obsah, nazev) {
    return '<label title="' + nazev + '"><input type="radio" name="' + skupina + '" value="' + id + '"'
      + (s[skupina === 'rezim' ? 'volba' : skupina] === id ? ' checked' : '') + ' aria-label="' + nazev + '">' + obsah + '</label>';
  }

  // Panel pro stav s a skutečný režim r (náhledy se kreslí v tomtéž režimu jako stránka)
  function panel(s, r) {
    var motiv = ' data-skin="' + s.skin + '" data-rezim="' + r + '"';
    var h = '<div class="vzhled-hlava"><h2>Vzhled a motivy</h2>'
      + '<button class="vzhled-zavrit" type="button" aria-label="Zavřít">×</button></div>';

    h += '<fieldset class="vzhled-rezim"><legend>Světlý / tmavý režim</legend><div class="vzhled-segmenty">';
    REZIMY.forEach(function (m) {
      h += moznost('rezim', m.id, s, '<span><svg viewBox="0 0 16 16" aria-hidden="true">' + m.ikona + '</svg>' + m.nazev + '</span>', m.nazev);
    });

    h += '</div></fieldset><fieldset class="vzhled-pozadi"><legend>Pozadí</legend><div class="vzhled-mrizka">'
      + moznost('pozadi', '', s, '<span class="vzhled-ctverec vzhled-cisty vzhled-podle-motivu"' + motiv + '></span>', 'Podle motivu');
    POZADI.forEach(function (p) {
      h += moznost('pozadi', p.id, s, '<span class="vzhled-ctverec" data-pozadi="' + p.id + '" data-rezim="' + r + '"></span>', p.nazev);
    });

    h += '</div></fieldset><fieldset class="vzhled-barvy"><legend>Základní barvy</legend><div class="vzhled-mrizka">'
      + moznost('akcent', '', s, '<span class="vzhled-kolecko vzhled-cisty vzhled-podle-motivu"' + motiv + '></span>', 'Podle motivu');
    AKCENTY.forEach(function (a) {
      h += moznost('akcent', a.id, s, '<span class="vzhled-kolecko" data-akcent="' + a.id + '"></span>', a.nazev);
    });

    h += '</div></fieldset><fieldset class="vzhled-motivy"><legend>Motivy</legend><div class="vzhled-mrizka">';
    SKINY.forEach(function (k) {
      h += moznost('skin', k.id, s, '<span class="vzhled-motiv vzhled-cisty" data-skin="' + k.id + '" data-rezim="' + r + '">'
        + '<span class="vzhled-mini"><i></i><b></b><b></b></span>'
        + '<span class="vzhled-motiv-nazev">' + k.nazev + '</span></span>', k.nazev);
    });
    return h + '</div></fieldset>';
  }

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SKINY: SKINY, AKCENTY: AKCENTY, POZADI: POZADI, REZIMY: REZIMY, stav: stav, rezim: rezim, panel: panel };
    return;
  }

  function nacti(klic) {
    try { return localStorage.getItem(klic); } catch (e) { return null; }
  }

  function uloz(klic, hodnota) {
    try {
      if (hodnota) localStorage.setItem(klic, hodnota); else localStorage.removeItem(klic);
    } catch (e) { /* bez úložiště platí volba jen do obnovení */ }
  }

  var koren = document.documentElement;
  var tmavySystem = matchMedia('(prefers-color-scheme: dark)');
  var s = stav({ skin: nacti('skin'), rezim: nacti('rezim'), akcent: nacti('akcent'), pozadi: nacti('pozadi') });

  var obal = document.querySelector('.vzhled');
  var tlacitko = obal.querySelector('.vzhled-tlacitko');
  var nabidka = obal.querySelector('.vzhled-panel');

  function atribut(jmeno, hodnota) {
    if (hodnota) koren.setAttribute(jmeno, hodnota); else koren.removeAttribute(jmeno);
  }

  // Zapíše stav na <html> a překreslí panel (náhledy závisí na motivu i režimu); fokus zůstane na téže volbě
  function pouzij() {
    var r = rezim(s.volba, tmavySystem.matches);
    koren.dataset.skin = s.skin;
    koren.dataset.rezim = r;
    atribut('data-akcent', s.akcent);
    atribut('data-pozadi', s.pozadi);
    var fokus = document.activeElement && nabidka.contains(document.activeElement) ? document.activeElement : null;
    var klic = fokus && fokus.name ? fokus.name + '=' + fokus.value : '';
    nabidka.innerHTML = panel(s, r);
    if (klic) {
      var znovu = nabidka.querySelector('input[name="' + klic.split('=')[0] + '"][value="' + klic.split('=')[1] + '"]');
      if (znovu) znovu.focus();
    }
  }

  pouzij();
  tmavySystem.addEventListener('change', pouzij);
  obal.hidden = false;

  function otevri(ano) {
    nabidka.hidden = !ano;
    tlacitko.setAttribute('aria-expanded', ano ? 'true' : 'false');
  }

  tlacitko.addEventListener('click', function () { otevri(nabidka.hidden); });

  nabidka.addEventListener('click', function (e) {
    if (e.target.closest('.vzhled-zavrit')) {
      otevri(false);
      tlacitko.focus();
    }
  });

  nabidka.addEventListener('change', function (e) {
    var klic = { skin: 'skin', rezim: 'volba', akcent: 'akcent', pozadi: 'pozadi' }[e.target.name];
    if (!klic) return;
    s[klic] = e.target.value;
    s = stav({ skin: s.skin, rezim: s.volba, akcent: s.akcent, pozadi: s.pozadi });
    uloz(e.target.name, e.target.name === 'rezim' ? s.volba : s[klic]);
    pouzij();
  });

  document.addEventListener('click', function (e) {
    // e.target.isConnected: klik na volbu panel překreslí, starý prvek pak už ve stránce není
    if (!nabidka.hidden && e.target.isConnected && !obal.contains(e.target)) otevri(false);
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !nabidka.hidden) {
      otevri(false);
      tlacitko.focus();
    }
  });
})();
