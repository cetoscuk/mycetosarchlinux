#!/usr/bin/env python3
import gi
import subprocess
import os
import threading

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

class WifiMenu(Gtk.Window):
    def __init__(self):
        super().__init__(title="mc-wifi-popup")
        self.set_wmclass("mc-wifi-popup", "mc-wifi-popup")
        self.set_role("mc-wifi-popup")
        self.set_type_hint(Gdk.WindowTypeHint.UTILITY)
        self.set_decorated(False)
        self.set_resizable(True)
        self.set_size_request(330, 440)
        self.set_keep_above(True)

        self.move(90, 60)
        self.connect("realize", lambda w: self.move(90, 60))

        # CSS Yükleyici
        provider = Gtk.CssProvider()
        css_path = os.path.expanduser("~/.config/waybar/mc-wifi.css")
        if os.path.exists(css_path):
            provider.load_from_path(css_path)
            Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(),
                provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

        # Ana Kutu
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        main_box.get_style_context().add_class("main-wrapper")
        self.add(main_box)

        # Üst Başlık (Sol: Switch, Sağ: X Butonu)
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        status_res = subprocess.run(["nmcli", "-fields", "WIFI", "g"], capture_output=True, text=True)
        wifi_on = "enabled" in status_res.stdout

        self.switch = Gtk.Switch()
        self.switch.set_active(wifi_on)
        self.switch.connect("state-set", self.on_switch_toggled)
        header.pack_start(self.switch, False, False, 0)

        title = Gtk.Label(label="Wi-Fi")
        title.get_style_context().add_class("title")
        header.pack_start(title, False, False, 0)

        close_btn = Gtk.Button(label="X")
        close_btn.get_style_context().add_class("close-btn")
        close_btn.connect("clicked", lambda w: Gtk.main_quit())
        header.pack_end(close_btn, False, False, 0)

        main_box.pack_start(header, False, False, 0)

        # Kaydırılabilir Ağ Listesi
        self.scroller = Gtk.ScrolledWindow()
        self.scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        main_box.pack_start(self.scroller, True, True, 0)

        self.list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.list_box.get_style_context().add_class("list-box")
        self.scroller.add(self.list_box)

        # Alt Çubuk (Sağ Altta Yenile Butonu)
        bottom_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.rescan_btn = Gtk.Button(label="Yenile")
        self.rescan_btn.get_style_context().add_class("rescan-btn")
        self.rescan_btn.connect("clicked", self.on_rescan_clicked)
        bottom_bar.pack_end(self.rescan_btn, False, False, 0)
        main_box.pack_start(bottom_bar, False, False, 0)

        self.active_details_widget = None
        self.load_networks(rescan=False)

        self.connect("destroy", Gtk.main_quit)

    def on_switch_toggled(self, switch, state):
        cmd = ["nmcli", "radio", "wifi", "on" if state else "off"]
        subprocess.run(cmd)

        for child in self.list_box.get_children():
            self.list_box.remove(child)

        if state:
            GLib.timeout_add(1200, self.finish_rescan)

    def on_rescan_clicked(self, btn):
        self.rescan_btn.set_label("Taraniyor...")
        self.rescan_btn.set_sensitive(False)

        def rescan_thread():
            subprocess.run(["nmcli", "dev", "wifi", "rescan"])
            GLib.idle_add(self.finish_rescan)

        threading.Thread(target=rescan_thread, daemon=True).start()

    def finish_rescan(self):
        for child in self.list_box.get_children():
            self.list_box.remove(child)
        self.load_networks(rescan=False)
        self.rescan_btn.set_label("Yenile")
        self.rescan_btn.set_sensitive(True)

    def get_known_connections(self):
        res = subprocess.run(["nmcli", "-t", "-f", "NAME,AUTOCONNECT", "connection", "show"], capture_output=True, text=True)
        known = {}
        for line in res.stdout.strip().split("\n"):
            parts = line.split(":")
            if len(parts) >= 2:
                known[parts[0]] = (parts[1].lower() == "yes")
        return known

    def load_networks(self, rescan=False):
        rescan_param = "yes" if rescan else "no"
        res = subprocess.run(
            ["nmcli", "-t", "-f", "IN-USE,SSID,SIGNAL,SECURITY", "device", "wifi", "list", "--rescan", rescan_param],
            capture_output=True,
            text=True
        )
        lines = [l for l in res.stdout.strip().split("\n") if l]
        known = self.get_known_connections()

        seen = set()
        for line in lines:
            parts = line.split(":")
            if len(parts) >= 4:
                in_use = (parts[0].strip() == "*")
                ssid = parts[1].strip()
                security = parts[3].strip()

                if not ssid or ssid in seen:
                    continue
                seen.add(ssid)

                is_saved = (ssid in known)
                auto_val = known.get(ssid, True)
                self.create_network_card(ssid, in_use, security, is_saved, auto_val)

        self.list_box.show_all()

    def create_network_card(self, ssid, in_use, security, is_saved, auto_val=True):
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        card.get_style_context().add_class("net-card")

        prefix = "[*] " if in_use else ""
        sec_text = " [Kilitli]" if (security and security != "--") else ""
        btn_text = f"{prefix}{ssid}{sec_text}"

        header_btn = Gtk.Button(label=btn_text)
        header_btn.get_style_context().add_class("net-btn")
        if in_use:
            header_btn.get_style_context().add_class("connected")

        details = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        details.get_style_context().add_class("details-box")
        details.set_visible(False)

        # Buton ve Durum İkonu İçin Yatay Kutu
        action_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        status_label = Gtk.Label(label="")
        status_label.set_visible(False)

        if in_use:
            disc_btn = Gtk.Button(label="Baglantiyi Kes")
            disc_btn.connect("clicked", lambda w, s=ssid, sl=status_label, b=disc_btn: self.start_disconnect(s, sl, b))
            action_row.pack_start(disc_btn, False, False, 0)
            action_row.pack_start(status_label, False, False, 0)
            details.pack_start(action_row, False, False, 0)
        else:
            auto_chk = Gtk.CheckButton(label="Otomatik baglan")
            auto_chk.set_active(auto_val)
            details.pack_start(auto_chk, False, False, 0)

            pwd_entry = None
            if security and security != "--" and not is_saved:
                pwd_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
                pwd_label = Gtk.Label(label="Ag guvenlik anahtari:")
                pwd_label.set_halign(Gtk.Align.START)
                pwd_box.pack_start(pwd_label, False, False, 0)

                pwd_entry = Gtk.Entry()
                pwd_entry.set_visibility(False)
                pwd_box.pack_start(pwd_entry, False, False, 0)
                details.pack_start(pwd_box, False, False, 0)

            conn_btn = Gtk.Button(label="Baglan")
            conn_btn.connect(
                "clicked",
                lambda w, s=ssid, p=pwd_entry, a=auto_chk, sec=bool(security and security != "--"), sav=is_saved, sl=status_label, b=conn_btn:
                self.start_connect(s, p, a, sec, sav, sl, b)
            )
            action_row.pack_start(conn_btn, False, False, 0)
            action_row.pack_start(status_label, False, False, 0)
            details.pack_start(action_row, False, False, 0)

        header_btn.connect("clicked", lambda w, d=details: self.toggle_details(d))

        card.pack_start(header_btn, False, False, 0)
        card.pack_start(details, False, False, 0)
        self.list_box.pack_start(card, False, False, 0)

    def toggle_details(self, details_box):
        is_open = details_box.get_visible()

        if self.active_details_widget and self.active_details_widget != details_box:
            self.active_details_widget.set_visible(False)

        if is_open:
            details_box.set_visible(False)
            self.active_details_widget = None
        else:
            details_box.set_visible(True)
            self.active_details_widget = details_box

    def start_connect(self, ssid, entry, auto_chk, has_sec, is_saved, status_lbl, btn):
        btn.set_sensitive(False)
        status_lbl.set_label("...")
        status_lbl.get_style_context().remove_class("status-ok")
        status_lbl.get_style_context().remove_class("status-err")
        status_lbl.set_visible(True)

        auto_val = "yes" if auto_chk.get_active() else "no"
        password = entry.get_text().strip() if entry else ""

        def connect_worker():
            success = False
            if is_saved:
                res = subprocess.run(["nmcli", "connection", "up", ssid], capture_output=True)
                success = (res.returncode == 0)
            elif has_sec and password:
                res = subprocess.run(["nmcli", "dev", "wifi", "connect", ssid, "password", password], capture_output=True)
                success = (res.returncode == 0)
            else:
                res = subprocess.run(["nmcli", "dev", "wifi", "connect", ssid], capture_output=True)
                success = (res.returncode == 0)

            if success:
                subprocess.run(["nmcli", "connection", "modify", ssid, "connection.autoconnect", auto_val])

            GLib.idle_add(self.apply_action_result, success, status_lbl, btn, True)

        threading.Thread(target=connect_worker, daemon=True).start()

    def start_disconnect(self, ssid, status_lbl, btn):
        btn.set_sensitive(False)
        status_lbl.set_label("...")
        status_lbl.get_style_context().remove_class("status-ok")
        status_lbl.get_style_context().remove_class("status-err")
        status_lbl.set_visible(True)

        def disconnect_worker():
            res = subprocess.run(["nmcli", "connection", "down", ssid], capture_output=True)
            success = (res.returncode == 0)
            GLib.idle_add(self.apply_action_result, success, status_lbl, btn, False)

        threading.Thread(target=disconnect_worker, daemon=True).start()

    def apply_action_result(self, success, status_lbl, btn, is_connect):
        btn.set_sensitive(True)
        if success:
            status_lbl.set_label("[✓]")
            status_lbl.get_style_context().add_class("status-ok")
            GLib.timeout_add(1000, self.finish_rescan)
        else:
            status_lbl.set_label("[✗]")
            status_lbl.get_style_context().add_class("status-err")

if __name__ == "__main__":
    win = WifiMenu()
    win.show_all()
    win.move(90, 60)
    Gtk.main()
