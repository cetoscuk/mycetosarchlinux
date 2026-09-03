#!/usr/bin/env bash

D="$HOME/.config/waybar/icons"

entries="Kapat\0icon\x1f$D/minecraft_red_bed.png\nYeniden Baslat\0icon\x1f$D/minecraft_compass.png\nAskiya Al\0icon\x1f$D/minecraft_lapis_lazuli.png\nCikis\0icon\x1f$D/minecraft_totem_of_undying.png"

chosen=$(echo -en "$entries" | rofi -dmenu -p "" -show-icons -theme ~/.config/waybar/enchant.rasi)

case "$chosen" in
    Kapat)
        systemctl poweroff
        ;;
    "Yeniden Baslat")
        systemctl reboot
        ;;
    "Askiya Al")
        systemctl suspend
        ;;
    Cikis)
        hyprctl dispatch exit
        ;;
esac
