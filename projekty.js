/* Sekce „Na čem pracuju“: vykreslí data/projekty.generated.json (tools/projekty.py). */
(function () {
  'use strict';

  var DEN = 86400000;

  function dnyOd(datum, dnes) {
    var dnesUtc = Date.UTC(dnes.getFullYear(), dnes.getMonth(), dnes.getDate());
    return Math.round((dnesUtc - Date.parse(datum + 'T00:00:00Z')) / DEN);
  }

  function pred(datum, dnes) {
    var d = dnyOd(datum, dnes);
    if (d <= 0) return 'dnes';
    if (d === 1) return 'včera';
    if (d < 7) return 'před ' + d + ' dny';
    var t = Math.floor(d / 7);
    if (d < 30) return t === 1 ? 'před týdnem' : 'před ' + t + ' týdny';
    var m = Math.floor(d / 30);
    if (m < 12) return m === 1 ? 'před měsícem' : 'před ' + m + ' měsíci';
    var r = Math.floor(d / 365);
    return r <= 1 ? 'před rokem' : 'před ' + r + ' lety';
  }

  function dniPrace(n) {
    if (n === 1) return '1 den práce';
    if (n >= 2 && n <= 4) return n + ' dny práce';
    return n + ' dní práce';
  }

  function esc(s) {
    var mapa = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
    return String(s).replace(/[&<>"']/g, function (z) { return mapa[z]; });
  }

  function datumCesky(iso) {
    var c = iso.split('-');
    return Number(c[2]) + '. ' + Number(c[1]) + '. ' + c[0];
  }

  function graf(tydny) {
    var max = Math.max.apply(null, tydny.concat([1]));
    var sirka = tydny.length * 8 - 2;
    var sloupky = tydny.map(function (n, i) {
      var v = n ? Math.max(3, Math.round(n / max * 24)) : 1;
      return '<rect x="' + i * 8 + '" y="' + (24 - v) + '" width="6" height="' + v +
        '" fill="' + (n ? '#000' : '#e2e2e2') + '"/>';
    }).join('');
    return '<svg class="projekty-graf" viewBox="0 0 ' + sirka + ' 24" width="' + sirka + '" height="24" role="img"' +
      ' aria-label="Commity po týdnech, nejstarší první: ' + tydny.join(', ') + '">' + sloupky + '</svg>';
  }

  function karta(k, dnes) {
    var odkaz = k.url ? '<a class="projekty-odkaz" href="' + esc(k.url) + '" target="_blank" rel="noopener"' +
      ' aria-label="' + esc(k.nazev) + ' na GitHubu">↗</a>' : '';
    return '<article class="projekty-karta">' +
      '<header><h3>' + esc(k.nazev) + '</h3>' +
      (k.jazyk ? '<span class="projekty-jazyk">' + esc(k.jazyk) + '</span>' : '') + '</header>' +
      (k.popis ? '<p class="projekty-popis">' + esc(k.popis) + '</p>' : '') +
      (k.stitky ? '<p class="projekty-stitky">' + k.stitky.map(esc).join(' · ') + '</p>' : '') +
      (k.tydny ? '<div class="projekty-aktivita">' + graf(k.tydny) + '<span>' + dniPrace(k.dni_prace) +
        '</span></div>' : '') +
      '<footer><time datetime="' + esc(k.posledni) + '" title="' + datumCesky(k.posledni) + '">naposledy ' +
      pred(k.posledni, dnes) + '</time>' + odkaz + '</footer>' +
      '</article>';
  }

  // Projekt s vlastním boxem přes celý řádek (Domácí server): seznam vybraných aplikací.
  function boxSamostatny(b, dnes) {
    var aplikace = (b.aplikace || []).map(function (a) {
      return '<li><h4>' + esc(a.nazev) + '</h4>' + (a.popis ? '<p>' + esc(a.popis) + '</p>' : '') + '</li>';
    }).join('');
    var aktivita = b.tydny ? '<div class="projekty-aktivita">' + graf(b.tydny) +
      '<span>' + dniPrace(b.dni_prace) + '</span></div>' : '';
    return '<article class="projekty-karta projekty-box">' +
      '<header><div><h3>' + esc(b.nazev) + '</h3>' +
      (b.popis ? '<p class="projekty-popis">' + esc(b.popis) + '</p>' : '') + '</div>' + aktivita + '</header>' +
      (aplikace ? '<ul class="projekty-aplikace">' + aplikace + '</ul>' : '') +
      (b.posledni ? '<footer><time datetime="' + esc(b.posledni) + '" title="' + datumCesky(b.posledni) +
        '">naposledy ' + pred(b.posledni, dnes) + '</time></footer>' : '') +
      '</article>';
  }

  function polozkaArchivu(a) {
    var nazev = a.url ? '<a href="' + esc(a.url) + '" target="_blank" rel="noopener">' + esc(a.nazev) + '</a>' : esc(a.nazev);
    var c = a.posledni ? a.posledni.split('-') : null;
    return '<li>' + nazev +
      (a.jazyk ? ' <span class="projekty-jazyk">' + esc(a.jazyk) + '</span>' : '') +
      (c ? ' <time datetime="' + esc(a.posledni) + '">' + Number(c[1]) + '/' + c[0] + '</time>' : '') + '</li>';
  }

  function vykresli(data, dnes) {
    var aktivni = (data && data.aktivni) || [];
    var archiv = (data && data.archiv) || [];
    var samostatne = (data && data.samostatne) || [];
    var starsi = (data && data.starsi) || [];
    if (!aktivni.length && !archiv.length && !samostatne.length && !starsi.length) return;
    if (starsi.length) {
      document.getElementById('projekty-starsi-grid').innerHTML =
        starsi.map(function (k) { return karta(k, dnes); }).join('');
      document.getElementById('projekty-starsi').hidden = false;
    }
    document.getElementById('projekty-grid').innerHTML =
      aktivni.map(function (k) { return karta(k, dnes); }).join('');
    document.getElementById('projekty-samostatne').innerHTML =
      samostatne.map(function (b) { return boxSamostatny(b, dnes); }).join('');
    if (archiv.length) {
      document.getElementById('projekty-archiv-pocet').textContent = archiv.length;
      document.getElementById('projekty-archiv-seznam').innerHTML = archiv.map(polozkaArchivu).join('');
      document.getElementById('projekty-archiv').hidden = false;
    }
    if (data.aktualizovano) {
      document.getElementById('projekty-data-k').textContent = 'Aktualizováno ' + datumCesky(data.aktualizovano);
    }
    document.getElementById('projekty').hidden = false;
  }

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { pred: pred, dniPrace: dniPrace, esc: esc, datumCesky: datumCesky, graf: graf,
      boxSamostatny: boxSamostatny, karta: karta };
    return;
  }

  fetch('data/projekty.generated.json', { cache: 'no-cache' })
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (data) { vykresli(data, new Date()); })
    .catch(function () { /* sekce zůstane skrytá */ });
})();
