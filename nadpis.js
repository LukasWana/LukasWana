// Nadpis „Lukáš Wana“ přesně na šířku podtitulu pod ním.
// Šířka textu závisí na písmu zařízení, proto se měří v prohlížeči. Zarovnává se
// inkoust písmen (canvas measureText), ne boxy: písmena mají po stranách volný
// prostor, který by u velkého nadpisu udělal viditelný rozdíl.
(function () {
  var nadpis = document.querySelector('.main-title');
  var podtitul = document.querySelector('.subtitle');
  if (!nadpis || !podtitul) return;
  var ctx = document.createElement('canvas').getContext('2d');

  function box(el) {
    var r = document.createRange();
    r.selectNodeContents(el);
    return { rect: r.getBoundingClientRect(), radku: r.getClientRects().length };
  }

  // Inkoust textu prvku při dané velikosti písma: odsazení zleva od začátku boxu a šířka.
  function inkoust(el, velikost) {
    var s = getComputedStyle(el);
    var text = el.textContent.trim();
    if (s.textTransform === 'uppercase') text = text.toUpperCase();
    ctx.font = s.fontWeight + ' ' + velikost + 'px ' + s.fontFamily;
    if ('letterSpacing' in ctx) {
      var ls = s.letterSpacing === 'normal' ? 0 : parseFloat(s.letterSpacing) * velikost / parseFloat(s.fontSize);
      ctx.letterSpacing = ls + 'px';
    }
    var m = ctx.measureText(text);
    return { vlevo: -m.actualBoundingBoxLeft, sirka: m.actualBoundingBoxLeft + m.actualBoundingBoxRight };
  }

  function prizpusob() {
    nadpis.style.left = '';
    var p = box(podtitul);
    if (!p.rect.width) return;
    var cilVlevo, cilSirka;
    if (p.radku > 1) {
      // Podtitul se zalomil (úzký displej): nadpis na šířku jeho řádků.
      cilVlevo = p.rect.left;
      cilSirka = p.rect.width;
    } else {
      var ip = inkoust(podtitul, parseFloat(getComputedStyle(podtitul).fontSize));
      cilVlevo = p.rect.left + ip.vlevo;
      cilSirka = ip.sirka;
    }
    // Inkoust roste lineárně s velikostí písma (letter-spacing je v em).
    var velikost = 100 * cilSirka / inkoust(nadpis, 100).sirka;
    nadpis.style.fontSize = velikost + 'px';
    var vlevo = box(nadpis).rect.left + inkoust(nadpis, velikost).vlevo;
    nadpis.style.left = (cilVlevo - vlevo) + 'px';
  }

  prizpusob();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(prizpusob);
  window.addEventListener('resize', prizpusob);
})();
