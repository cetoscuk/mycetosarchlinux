<p align="right">
  <a href="README.md">English</a> | <b>Türkçe</b>
</p>

# Arch Linux + Hyprland (Lua) Rice

Lua tabanlı Hyprland, şeffaf Conky sistem izleyicisi, Waybar ve Rofi ile güçlendirilmiş hafif ve hızlı Arch Linux masaüstü ortamı. Bunu yaparken ağır bir şekilde yapay zeka kullandım. Buradaki bilgi kısmını da yapay zekaya yazdırdım. Bu rice'ı diğer cihazlarımda da kullanabilmek amacıyla buraya yükledim. İstediğiniz gibi kullanabilirsiniz. Eğer herhangi bir sorunla karşılaşırsanız bana raporlayabilirsiniz. Düzeltebilirim.

---

## 🚀 Hızlı Kurulum

Sıfır bir Arch Linux sisteminde terminali açıp şu komutları çalıştırmanız yeterlidir:

```bash
git clone https://github.com/cetoscuk/mycetosarchlinux.git ~/dotfiles
cd ~/dotfiles && ./install.sh
```

---

## 🛠️ Özellikler ve Araçlar

* **Pencere Yöneticisi:** Hyprland (`hyprland.lua` yapılandırması)
* **Durum Çubuğu:** Waybar
* **Uygulama Menüsü:** Rofi (`Super + R`)
* **Sistem İzleyici:** Conky (Sağ alt köşe, tamamen şeffaf arka plan)
* **Ofis:** LibreOffice (Microsoft Core Fonts desteğiyle)
* **Oyun:** Steam ve Prism Launcher (Minecraft)

---

## ⌨️ Kısayollar

| Kısayol | İşlev |
| :--- | :--- |
| `Super + Q` | Terminal aç |
| `Super + C` | Aktif pencereyi kapat |
| `Super + R` | Uygulama menüsü (Rofi) |
| `Super + V` | Serbest pencere (Float) modunu aç/kapat |
| `Super + F` | Tam ekran |
| `Super + [1-9]` | Çalışma alanına geç |
| `Super + Shift + [1-9]` | Pencereyi çalışma alanına taşı |

---

## 📦 `install.sh` Neler Yapar?

1. Temel masaüstü paketlerini, fontları (DejaVu, Noto, AUR üzerinden MS Fonts) ve araçları yükler.
2. Sistemde yoksa `yay` (AUR yardımcısı) kurulumunu otomatik tamamlar.
3. `hypr`, `conky`, `waybar` ve `rofi` ayar klasörlerini sembolik bağ (symlink) ile `~/.config/` altına bağlar.
