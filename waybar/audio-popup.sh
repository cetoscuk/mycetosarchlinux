#!/usr/bin/env bash

# Panel açıksa kapat (Toggle)
if pgrep -f "rofi.*audio-card.rasi" > /dev/null; then
    killall rofi
    exit 0
fi

# Ses düzeyini oku
VOL_RAW=$(wpctl get-volume @DEFAULT_AUDIO_SINK@ | awk '{print $2}')
VOL=$(awk -v v="$VOL_RAW" 'BEGIN { printf "%.0f", v * 100 }')
MUTED=$(wpctl get-volume @DEFAULT_AUDIO_SINK@ | grep -q "MUTED" && echo " [SESSIZ]" || echo "")

# 10 kademeli görsel bar
FILLED=$((VOL / 10))
[ $FILLED -gt 10 ] && FILLED=10
EMPTY=$((10 - FILLED))
BAR=""
for ((i=0; i<FILLED; i++)); do BAR="${BAR}■"; done
for ((i=0; i<EMPTY; i++)); do BAR="${BAR}□"; done

MENU="[${BAR}] %${VOL}${MUTED}
+ Sesi Artir (%5)
- Sesi Azalt (%5)
Sesi Sustur / Ac
Cikis Aygiti Sec"

CHOSEN=$(echo -e "$MENU" | rofi -dmenu -p "SES AYARI" -theme ~/.config/waybar/audio-card.rasi)

case "$CHOSEN" in
    "["*"]"*)
        # Bara tıklandığında hızlı yüzde menüsü aç veya döngüsel artır
        wpctl set-volume @DEFAULT_AUDIO_SINK@ 10%+
        exec "$0"
        ;;
    "+ Sesi Artir (%5)")
        wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%+
        exec "$0"
        ;;
    "- Sesi Azalt (%5)")
        wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-
        exec "$0"
        ;;
    "Sesi Sustur / Ac")
        wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle
        exec "$0"
        ;;
    "Cikis Aygiti Sec")
        SINKS=$(wpctl status | sed -n '/Sinks:/,/Sources:/p' | grep -E '│.*[0-9]+\.' | sed 's/│//g; s/^[ \t]*//')
        DEVICE=$(echo "$SINKS" | rofi -dmenu -p "Aygit:" -theme ~/.config/waybar/audio-card.rasi)
        if [ -n "$DEVICE" ]; then
            ID=$(echo "$DEVICE" | grep -oP '(?<=[* ])[0-9]+(?=\.)')
            [ -z "$ID" ] && ID=$(echo "$DEVICE" | awk '{print $1}' | tr -d '.')
            wpctl set-default "$ID"
        fi
        exec "$0"
        ;;
esac
