#!/usr/bin/env bash

# Dunst geçmişini çek
HISTORY=$(dunstctl history)

# Bildirim yoksa uyar
if [ "$HISTORY" = '{"data":[[]]}' ] || [ -z "$HISTORY" ]; then
    notify-send "Bildirim Merkezi" "Geçmiş bildirim bulunmuyor."
    exit 0
fi

# JSON'dan mesajları formatlayarak al
NOTIFS=$(echo "$HISTORY" | python3 -c '
import sys, json

try:
    data = json.load(sys.stdin)["data"][0]
    for item in data:
        app = item.get("appname", {}).get("data", "Sistem")
        summary = item.get("summary", {}).get("data", "")
        body = item.get("body", {}).get("data", "").replace("\n", " ")
        print(f"[{app}] {summary}: {body}".strip())
except Exception:
    pass
')

# Rofi menüsünü Monocraft fontuyla aç
CHOSEN=$(echo -e "🗑️ Geçmişi Temizle\n$NOTIFS" | rofi -dmenu -i -p "Bildirimler" -theme-str 'configuration { font: "Monocraft 11"; } window { width: 500px; border-radius: 10px; }')

# Temizle seçildiyse geçmişi sil
if [ "$CHOSEN" = "🗑️ Geçmişi Temizle" ]; then
    dunstctl history-clear
    notify-send "Bildirim Merkezi" "Tüm geçmiş temizlendi."
fi

