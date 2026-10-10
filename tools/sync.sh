#!/bin/sh
# Hodinová aktualizace přehledu projektů (cron na asus-server).
# zdroj = veřejný klon LukasWana (jen čtení); web = klon LukasWana/web (deploy key, zápis).
# Návrh: docs/plans/2026-10-10-projekty-design.md
set -eu

main() {
    ZDROJ="$HOME/lukaswana-web/zdroj"
    WEB="$HOME/lukaswana-web/web"
    KONFIG="$HOME/.config/lukaswana-web"
    LOG="$HOME/.local/state/lukaswana-web/sync.log"
    mkdir -p "$(dirname "$LOG")"
    if [ -f "$LOG" ] && [ "$(wc -c < "$LOG")" -gt 1048576 ]; then
        mv "$LOG" "$LOG.1"
    fi
    exec >>"$LOG" 2>&1
    echo "== $(date -Is)"
    git -C "$ZDROJ" pull --ff-only --quiet
    git -C "$WEB" fetch --quiet origin
    git -C "$WEB" reset --quiet --hard origin/main
    python3 "$ZDROJ/tools/projekty.py" --token-soubor "$KONFIG/token" --skryt-soubor "$KONFIG/skryt.txt" --vystup "$WEB/data/projekty.generated.json"
    if [ -z "$(git -C "$WEB" status --porcelain -- data)" ]; then
        echo "beze změny"
        return 0
    fi
    git -C "$WEB" add data/projekty.generated.json
    git -C "$WEB" commit --quiet -m "data: projekty (asus-server)"
    if git -C "$WEB" push --quiet; then
        echo "pushnuto $(git -C "$WEB" rev-parse --short HEAD)"
        return 0
    fi
    # Souběh s deployem z repa LukasWana (ten pushuje do webu taky). Deploy data/ nemění,
    # takže stačí vzít vygenerovaný soubor, postavit ho na čerstvý origin/main a pushnout znovu.
    echo "push odmítnut, opakuji nad čerstvým origin/main"
    DATA="$(mktemp)"
    cp "$WEB/data/projekty.generated.json" "$DATA"
    git -C "$WEB" fetch --quiet origin
    git -C "$WEB" reset --quiet --hard origin/main
    cp "$DATA" "$WEB/data/projekty.generated.json"
    rm -f "$DATA"
    if [ -z "$(git -C "$WEB" status --porcelain -- data)" ]; then
        echo "beze změny"
        return 0
    fi
    git -C "$WEB" add data/projekty.generated.json
    git -C "$WEB" commit --quiet -m "data: projekty (asus-server)"
    git -C "$WEB" push --quiet
    echo "pushnuto $(git -C "$WEB" rev-parse --short HEAD)"
}

# Celé tělo je ve funkci: sh čte skript postupně a `git pull` výše může tenhle soubor
# změnit během běhu. Funkce se načte celá dřív, než se spustí.
main "$@"
exit
