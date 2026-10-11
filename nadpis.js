// Řada ikon sítí pod nadpisem „Lukáš Wana“ přesně na šířku jeho písmen.
// Nadpis má pevnou velikost (style.css); šířka písmen ale závisí na písmu zařízení, proto se měří
// v prohlížeči. Měří se inkoust písmen (canvas measureText), ne box: písmena mají po stranách volný
// prostor, který by u velkého nadpisu udělal viditelný rozdíl.
(function () {
  var nadpis = document.querySelector('.main-title');
  var ikony = document.querySelector('.hlava-ikony');
  if (!nadpis || !ikony) return;
  var ctx = document.createElement('canvas').getContext('2d');

  // Inkoust textu nadpisu: odsazení zleva od začátku boxu textu a šířka.
  function inkoust(el) {
    var s = getComputedStyle(el);
    var text = el.textContent.trim();
    if (s.textTransform === 'uppercase') text = text.toUpperCase();
    ctx.font = s.fontWeight + ' ' + s.fontSize + ' ' + s.fontFamily;
    if ('letterSpacing' in ctx) ctx.letterSpacing = s.letterSpacing === 'normal' ? '0px' : s.letterSpacing;
    var m = ctx.measureText(text);
    return { vlevo: -m.actualBoundingBoxLeft, sirka: m.actualBoundingBoxLeft + m.actualBoundingBoxRight };
  }

  function prizpusob() {
    ikony.style.left = '';
    var r = document.createRange();
    r.selectNodeContents(nadpis);
    var box = r.getBoundingClientRect();
    if (!box.width) return;
    var ink = inkoust(nadpis);
    var pocet = ikony.children.length;
    var mezera = parseFloat(getComputedStyle(ikony).columnGap) || 0;
    ikony.style.setProperty('--hlava-ikona', (ink.sirka - (pocet - 1) * mezera) / pocet + 'px');
    // Řada je na středu (flex center): posunout její střed pod střed písmen, ne boxu nadpisu.
    var radek = ikony.getBoundingClientRect();
    ikony.style.left = (box.left + ink.vlevo + ink.sirka / 2 - (radek.left + radek.width / 2)) + 'px';
  }

  prizpusob();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(prizpusob);
  window.addEventListener('resize', prizpusob);
})();
