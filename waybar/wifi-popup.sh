#!/usr/bin/env bash

# Menü zaten açıksa kapat (Toggle)
if pgrep -f "rofi.*wifi-card.rasi" > /dev/null; then
    killall rofi
    exit 0
fi

# Wi-Fi durumunu al
WIFI_STATUS=$(nmcli -fields WIFI g | tail -n 1 | tr -d ' ')

if [ "$WIFI_STATUS" = "enabled" ]; then
    TOGGLE_TEXT="Wi-Fi Kapat"
else
    TOGGLE_TEXT="Wi-Fi Ac"
fi

# Mevcut bağlı olunan ağ
ACTIVE_SSID=$(nmcli -t -f active,ssid dev wifi | grep '^yes' | cut -d: -f2)
[ -z "$ACTIVE_SSID" ] && ACTIVE_SSID="Bagli Degil"

# Ağları tara ve listele (tekrar edenleri filtrele)
LIST=$(nmcli --fields IN-USE,SSID,SIGNAL,SECURITY device wifi list | sed 1d | sed 's/^yes/\*/; s/^no/ /' | awk '!seen[$2]++')

HEADER="Durum: $ACTIVE_SSID\n$TOGGLE_TEXT\nAglar Yenile"
MENU=$(echo -e "$HEADER\n$LIST")

CHOSEN=$(echo -e "$MENU" | rofi -dmenu -p "WI-FI" -theme ~/.config/waybar/wifi-card.rasi)

[ -z "$CHOSEN" ] && exit 0

case "$CHOSEN" in
    "Wi-Fi Kapat")
        nmcli radio wifi off
        ;;
    "Wi-Fi Ac")
        nmcli radio wifi on
        ;;
    "Aglar Yenile")
        nmcli dev wifi rescan
        exec "$0"
        ;;
    "Durum: "*)
        exec "$0"
        ;;
    *)
        # Seçilen ağ adını ayıkla
        SSID=$(echo "$CHOSEN" | awk '{print $2}')
        [ -z "$SSID" ] && exit 0

        # Ağ zaten kayıtlı mı kontrol et
        if nmcli -s -g NAME connection show | grep -Fxq "$SSID"; then
            nmcli connection up "$SSID"
        else
            # Güvenlik korumalıysa şifre sor
            SEC=$(echo "$CHOSEN" | grep -iE 'wpa|wep|802.1x')
            if [ -n "$SEC" ]; then
                PASS=$(rofi -dmenu -p "Sifre ($SSID):" -password -theme ~/.config/waybar/wifi-card.rasi)
                [ -n "$PASS" ] && nmcli dev wifi connect "$SSID" password "$PASS"
            else
                nmcli dev wifi connect "$SSID"
            fi
        fi
        ;;
esac
