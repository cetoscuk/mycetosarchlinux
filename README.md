<p align="right">
  <b>English</b> | <a href="README_TR.md">Türkçe</a>
</p>

# Arch Linux + Hyprland (Lua) Rice

A lightweight, performant, and aesthetic Arch Linux desktop environment powered by Lua-configured Hyprland, a transparent Conky system monitor, Waybar, and Rofi. I have used AI heavyly while creating this. Even this information was made by AI. I'm updloading this so that I may use this rice on different devices of mine. Feel free to use it as well. If you have any problems with it, just report it to me. I might fix it.

---

## 🚀 Quick Install

On a fresh Arch Linux installation, open your terminal and run:
bash
git clone https://github.com/cetoscuk/mycetosarchlinux.git ~/dotfiles
cd ~/dotfiles && ./install.sh---

# Arch Linux + Hyprland (Lua) Rice

A lightweight, performant, and aesthetic Arch Linux desktop environment powered by Lua-configured Hyprland, a transparent Conky system monitor, Waybar, and Rofi.

---

## 🚀 Quick Install

On a fresh Arch Linux installation, open your terminal and run:bash
git clone https://github.com/cetoscuk/mycetosarchlinux.git ~/dotfiles
cd ~/dotfiles && ./install.sh---

## 🛠️ Features & Components

* **Window Manager:** Hyprland (`hyprland.lua` configuration)
* **Status Bar:** Waybar
* **Application Launcher:** Rofi (`Super + R`)
* **System Monitor:** Conky (Bottom-right, fully transparent background)
* **Productivity:** LibreOffice (bundled with Microsoft Core Fonts)
* **Gaming:** Steam & Prism Launcher (Minecraft)

---

## ⌨️ Keybindings

| Shortcut | Action |
| :--- | :--- |
| `Super + Q` | Launch Terminal |
| `Super + C` | Close Active Window |
| `Super + R` | Application Launcher (Rofi) |
| `Super + V` | Toggle Floating Mode |
| `Super + F` | Toggle Fullscreen |
| `Super + [1-9]` | Switch Workspace |
| `Super + Shift + [1-9]` | Move Window to Workspace |

---

## 📦 What `install.sh` Does

1. Installs base graphical packages, fonts (DejaVu, Noto, MS Fonts via AUR), and utilities.
2. Installs `yay` (AUR helper) automatically if not detected.
3. Links `hypr`, `conky`, `waybar`, and `rofi` configuration directories into `~/.config/` using symlinks.
