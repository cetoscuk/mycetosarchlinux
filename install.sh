#!/usr/bin/env bash
set -e

echo "=== Arch Linux Rice Kurulumu Başlatılıyor ==="

# Temel paketler, fontlar ve araçlar
sudo pacman -S --needed --noconfirm \
    hyprland waybar rofi conky git \
    ttf-liberation ttf-dejavu noto-fonts \
    libreoffice-fresh prismlauncher jre-openjdk jre17-openjdk

# AUR yardımcısı (yay) yoksa kuralım
if ! command -v yay &> /dev/null; then
    echo "AUR yardımcısı (yay) kuruluyor..."
    git clone https://aur.archlinux.org/yay-bin.git /tmp/yay-bin
    cd /tmp/yay-bin && makepkg -si --noconfirm
    cd -
fi

# MS Fontları AUR üzerinden kur
yay -S --needed --noconfirm ttf-ms-fonts

# Config klasörlerini sembolik bağ ile bağla
mkdir -p ~/.config
for dir in hypr conky waybar rofi; do
    if [ -d "$PWD/$dir" ]; then
        rm -rf ~/.config/"$dir"
        ln -sf "$PWD/$dir" ~/.config/"$dir"
        echo "[+] ~/.config/$dir bağlandı."
    fi
done

echo "=== Kurulum tamamlandı! Hyprland'i başlatabilirsiniz. ==="
