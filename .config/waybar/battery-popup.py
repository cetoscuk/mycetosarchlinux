#!/usr/bin/env python3
import subprocess
import os
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

class BatteryPopup(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("mc-battery-popup")
        self.set_wmclass("mc-battery-popup", "mc-battery-popup")
        self.set_default_size(320, 360)
        self.set_decorated(False)
        self.set_skip_taskbar_hint(True)
        self.set_modal(True)

        self.connect("delete-event", lambda w, e: Gtk.main_quit())
        self.connect("button-press-event", self.on_window_clicked)

        css = """
        * {
            font-family: "Monocraft";
            font-size: 13px;
            color: #cdd6f4;
        }
        window {
            background-color: #11111b;
            border: 2px solid #a6e3a1;
            border-radius: 8px;
        }
        #header {
            padding: 10px;
            border-bottom: 1px solid #313244;
        }

        button {
            background-image: none;
            background-color: transparent;
            border: none;
            box-shadow: none;
            text-shadow: none;
            outline: none;
        }

        #close-btn {
            background-image: none;
            background-color: #1e1e2e;
            border: 1px solid #313244;
            color: #f38ba8;
            font-weight: bold;
            font-size: 14px;
            padding: 2px 10px;
            border-radius: 6px;
        }
        #close-btn:hover {
            background-image: -gtk-gradient(linear, left top, right top, from(rgba(110, 50, 140, 0.6)), to(rgba(166, 227, 161, 0.4)));
            border-color: #a6e3a1;
            color: #ffffff;
        }

        .bat-card {
            background-color: #181825;
            border: 1px solid #313244;
            border-radius: 6px;
            padding: 12px;
            margin: 8px 12px;
        }

        .bat-percentage {
            font-size: 26px;
            font-weight: bold;
            color: #a6e3a1;
        }

        .bat-status {
            font-size: 12px;
            color: #bac2de;
        }

        .section-title {
            color: #a6e3a1;
            font-weight: bold;
            padding: 4px 14px 2px 14px;
        }

        .profile-btn {
            background-image: none;
            background-color: #181825;
            border: 1px solid #313244;
            border-radius: 6px;
            padding: 10px;
            margin: 4px 12px;
        }

        .profile-btn:hover {
            background-image: -gtk-gradient(linear, left top, right top, from(rgba(110, 50, 140, 0.5)), to(rgba(166, 227, 161, 0.3)));
            border-color: #a6e3a1;
            color: #ffffff;
        }

        .profile-btn.active {
            border: 2px solid #a6e3a1;
            background-color: #1e1e2e;
        }
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css.encode("utf-8"))
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.add(main_box)

        # Üst Başlık ve Kapat Butonu
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        header.set_name("header")
        main_box.pack_start(header, False, False, 0)

        title = Gtk.Label(label="💎 Güç & Pil Yönetimi")
        header.pack_start(title, False, False, 0)

        close_btn = Gtk.Button(label="✕")
        close_btn.set_name("close-btn")
        close_btn.connect("clicked", lambda w: Gtk.main_quit())
        header.pack_end(close_btn, False, False, 0)

        # Windows Tarzı Pil Bilgi Kartı
        bat_percent, bat_status = self.get_battery_info()
        card_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        card_box.get_style_context().add_class("bat-card")

        pct_label = Gtk.Label(label=bat_percent)
        pct_label.get_style_context().add_class("bat-percentage")
        pct_label.set_xalign(0)
        card_box.pack_start(pct_label, False, False, 0)

        st_label = Gtk.Label(label=bat_status)
        st_label.get_style_context().add_class("bat-status")
        st_label.set_xalign(0)
        card_box.pack_start(st_label, False, False, 0)

        main_box.pack_start(card_box, False, False, 0)

        # Güç Modu Seçenekleri
        p_title = Gtk.Label(label="Güç Modu:")
        p_title.get_style_context().add_class("section-title")
        p_title.set_xalign(0)
        main_box.pack_start(p_title, False, False, 0)

        current_profile = self.get_current_profile()

        profiles = [
            ("power-saver", "🌱 En İyi Güç Tasarrufu"),
            ("balanced", "⚖️ Dengeli"),
            ("performance", "⚡ En İyi Performans")
        ]

        for p_id, p_label in profiles:
            btn = Gtk.Button(label=p_label)
            btn.get_style_context().add_class("profile-btn")
            if current_profile == p_id:
                btn.get_style_context().add_class("active")
            btn.connect("clicked", self.set_profile, p_id)
            main_box.pack_start(btn, False, False, 0)

    def on_window_clicked(self, widget, event):
        alloc = self.get_allocation()
        if not (0 <= event.x <= alloc.width and 0 <= event.y <= alloc.height):
            Gtk.main_quit()
        return False

    def get_battery_info(self):
        bat_dir = "/sys/class/power_supply"
        percent = "Bilinmiyor"
        status = "Deşarj Oluyor"
        try:
            bats = [b for b in os.listdir(bat_dir) if b.startswith("BAT")]
            if bats:
                b = bats[0]
                with open(f"{bat_dir}/{b}/capacity", "r") as f:
                    percent = f"%{f.read().strip()}"
                with open(f"{bat_dir}/{b}/status", "r") as f:
                    raw_st = f.read().strip()
                    if raw_st == "Charging":
                        status = "Prize takılı, şarj ediliyor"
                    elif raw_st == "Full":
                        status = "Tam dolu"
                    else:
                        status = "Pille çalışıyor"
        except Exception:
            pass
        return percent, status

    def get_current_profile(self):
        try:
            out = subprocess.check_output(["powerprofilesctl", "get"]).decode().strip()
            return out
        except Exception:
            return "balanced"

    def set_profile(self, widget, profile_name):
        try:
            subprocess.run(["powerprofilesctl", "set", profile_name])
        except Exception:
            pass
        Gtk.main_quit()

win = BatteryPopup()
win.show_all()

display = Gdk.Display.get_default()
seat = display.get_default_seat()
seat.grab(win.get_window(), Gdk.SeatCapabilities.ALL, True, None, None, None)

Gtk.main()
