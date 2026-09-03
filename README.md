<img width="1920" height="1080" alt="screenshot_2026-09-04_01-09-49" src="https://github.com/user-attachments/assets/5c917fcc-5082-4900-a0c4-415ce699d137" />
<p align="right">
  <b>English</b> | <a href="README_TR.md">Türkçe</a>
</p>

# Arch Linux + Hyprland (Lua) Rice

A lightweight, performant, and aesthetic Arch Linux desktop environment powered by Lua-configured Hyprland, a transparent Conky system monitor, Waybar, and Rofi. You can see that the calendar is in English but ram info is in Turkish. That's because I am bilingual and just prefer one language over another sometimes. So, some GUI elements might be in Turkish. I heavily utilized artificial intelligence while building this setup and generating this documentation. I uploaded this rice here primarily to replicate my setup across my other devices. Feel free to use and modify it as you like. If you encounter any issues, feel free to report them and I'll look into fixing them.

---

## 🚀 Quick Install

On a fresh Arch Linux installation, open your terminal and run:

```bash
git clone https://github.com/cetoscuk/mycetosarchlinux.git ~/dotfiles
cd ~/dotfiles && ./install.sh
```

---

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
| `Super + Q` | Open Terminal |
| `Super + C` | Close Active Window |
| `Super + R` | Application Launcher (Rofi) |
| `Super + V` | Toggle Floating Mode |
| `Super + F` | Toggle Fullscreen |
| `Super + [1-9]` | Switch Workspace |
| `Super + Shift + [1-9]` | Move Window to Workspace |

---

## 📦 What `install.sh` Does

1. Installs base graphical packages, fonts (DejaVu, Noto, MS Fonts via AUR), and productivity/gaming tools.
2. Automatically sets up `yay` (AUR helper) if not already present.
3. Automatically creates symbolic links (`symlinks`) for `hypr`, `conky`, `waybar`, and `rofi` directories into `~/.config/`.
