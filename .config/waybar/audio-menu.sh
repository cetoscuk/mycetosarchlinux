#!/usr/bin/env bash

# Mevcut ses seviyesini hesapla
VOL_RAW=$(wpctl get-volume @DEFAULT_AUDIO_SINK@ | awk '{print $2}')
VOL=$(awk -v v="$VOL_RAW" 'BEGIN { printf "%.0f", v * 100 }')
MUTED=$(wpctl get-volume @DEFAULT_AUDIO_SINK@ | grep -q "MUTED" && echo " [SESSIZ]" || echo "")

# 10 kademeli soldan sağa gösterge çubuğu
FILLED=$((VOL / 10))
[ $FILLED -gt 10 ] && FILLED=10
EMPTY=$((10 - FILLED))
BAR=""
for ((i=0; i<FILLED; i++)); do BAR="${BAR}■"; done
for ((i=0; i<EMPTY; i++)); do BAR="${BAR}□"; done

# Aktif ses çıkış cihazını bul
CURRENT_SINK=$(wpctl status | sed -n '/Sinks:/,/Sources:/p' | grep '\*' | sed 's/.*[0-9]\+\.\s*//; s/\[.*//')

MENU="Ses: [${BAR}] ${VOL}%${MUTED}
+ Ses Artir (+5%)
- Ses Azalt (-5%)
M Sesi Kapat/Ac
Cikis Aygiti Degistir (${CURRENT_SINK:0:15}...)"

CHOSEN=$(echo -e "$MENU" | rofi -dmenu -p "SES AYARI" -theme ~/.config/waybar/audio.rasi)

case "$CHOSEN" in
    "+ Ses Artir (+5%)")
        wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%+
        exec "$0"
        ;;
    "- Ses Azalt (-5%)")
        wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-
        exec "$0"
        ;;
    "M Sesi Kapat/Ac")
        wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle
        exec "$0"
        ;;
    "Cikis Aygiti Degistir"*)
        SINKS=$(wpctl status | sed -n '/Sinks:/,/Sources:/p' | grep -E '│.*[0-9]+\.' | sed 's/│//g; s/^[ \t]*//')
        DEVICE=$(echo "$SINKS" | rofi -dmenu -p "AYGIT SEC:" -theme ~/.config/waybar/audio.rasi)
        if [ -n "$DEVICE" ]; then
            ID=$(echo "$DEVICE" | grep -oP '(?<=[* ])[0-9]+(?=\.)')
            [ -z "$ID" ] && ID=$(echo "$DEVICE" | awk '{print $1}' | tr -d '.')
            wpctl set-default "$ID"
        fi
        exec "$0"
        ;;
esac
