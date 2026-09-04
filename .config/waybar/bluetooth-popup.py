#!/usr/bin/env python3
import gi
import subprocess
import os
import threading
import re
import time

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

class BluetoothMenu(Gtk.Window):
    def __init__(self):
        super().__init__(title="mc-bluetooth-popup")
        self.set_wmclass("mc-bluetooth-popup", "mc-bluetooth-popup")
        self.set_role("mc-bluetooth-popup")
        self.set_type_hint(Gdk.WindowTypeHint.UTILITY)
        self.set_decorated(False)
        self.set_resizable(True)
        self.set_size_request(330, 460)
        self.set_keep_above(True)

        self.move(95, 430)
        self.connect("realize", lambda w: self.move(95, 430))

        # CSS Yükleyici (Wi-Fi ile aynı tema)
        provider = Gtk.CssProvider()
        css_path = os.path.expanduser("~/.config/waybar/mc-wifi.css")
        if os.path.exists(css_path):
            provider.load_from_path(css_path)
            Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(),
                provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        main_box.get_style_context().add_class("main-wrapper")
        self.add(main_box)

        # Üst Başlık (Sol: Switch, Başlık, Sağ: X Butonu)
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        status_res = subprocess.run(["bluetoothctl", "show"], capture_output=True, text=True)
        bt_on = "Powered: yes" in status_res.stdout

        self.switch = Gtk.Switch()
        self.switch.set_active(bt_on)
        self.switch.connect("state-set", self.on_switch_toggled)
        header.pack_start(self.switch, False, False, 0)

        title = Gtk.Label(label="Bluetooth")
        title.get_style_context().add_class("title")
        header.pack_start(title, False, False, 0)

        close_btn = Gtk.Button(label="X")
        close_btn.get_style_context().add_class("close-btn")
        close_btn.connect("clicked", lambda w: Gtk.main_quit())
        header.pack_end(close_btn, False, False, 0)

        main_box.pack_start(header, False, False, 0)

        # Kaydırılabilir Liste
        self.scroller = Gtk.ScrolledWindow()
        self.scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        main_box.pack_start(self.scroller, True, True, 0)

        self.list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.list_box.get_style_context().add_class("list-box")
        self.scroller.add(self.list_box)

        # Alt Çubuk (Yenile Butonu)
        bottom_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.rescan_btn = Gtk.Button(label="Yenile")
        self.rescan_btn.get_style_context().add_class("rescan-btn")
        self.rescan_btn.connect("clicked", self.on_rescan_clicked)
        bottom_bar.pack_end(self.rescan_btn, False, False, 0)
        main_box.pack_start(bottom_bar, False, False, 0)

        self.active_details_widget = None

        # Görünürlüğü aç
        subprocess.run(["bluetoothctl", "discoverable", "on"], capture_output=True)
        subprocess.run(["bluetoothctl", "pairable", "on"], capture_output=True)

        self.load_devices()
        self.connect("destroy", Gtk.main_quit)

    def on_switch_toggled(self, switch, state):
        cmd = ["bluetoothctl", "power", "on" if state else "off"]
        subprocess.run(cmd)

        for child in self.list_box.get_children():
            self.list_box.remove(child)

        if state:
            subprocess.run(["bluetoothctl", "discoverable", "on"], capture_output=True)
            GLib.timeout_add(1000, self.finish_rescan)

    def on_rescan_clicked(self, btn):
        self.rescan_btn.set_label("Taraniyor...")
        self.rescan_btn.set_sensitive(False)

        def rescan_thread():
            subprocess.run(["bluetoothctl", "discoverable", "on"], capture_output=True)
            subprocess.run(["bluetoothctl", "--timeout", "6", "scan", "on"], capture_output=True)
            GLib.idle_add(self.finish_rescan)

        threading.Thread(target=rescan_thread, daemon=True).start()

    def finish_rescan(self):
        for child in self.list_box.get_children():
            self.list_box.remove(child)
        self.load_devices()
        self.rescan_btn.set_label("Yenile")
        self.rescan_btn.set_sensitive(True)

    def load_devices(self):
        res = subprocess.run(["bluetoothctl", "devices"], capture_output=True, text=True)
        lines = [l for l in res.stdout.strip().split("\n") if l]

        conn_res = subprocess.run(["bluetoothctl", "devices", "Connected"], capture_output=True, text=True)
        connected_macs = set(re.findall(r"([0-9A-Fa-f:]{17})", conn_res.stdout))

        # Eşleşmiş cihazları al
        paired_res = subprocess.run(["bluetoothctl", "devices", "Paired"], capture_output=True, text=True)
        paired_macs = set(re.findall(r"([0-9A-Fa-f:]{17})", paired_res.stdout))

        for line in lines:
            parts = line.split(" ", 2)
            if len(parts) >= 3:
                mac = parts[1]
                name = parts[2]
                if name.replace("-", ":") == mac:
                    continue
                is_connected = (mac in connected_macs)
                is_paired = (mac in paired_macs)
                self.create_device_card(mac, name, is_connected, is_paired)

        self.list_box.show_all()

    def create_device_card(self, mac, name, is_connected, is_paired):
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        card.get_style_context().add_class("net-card")

        prefix = "[*] " if is_connected else ""
        header_btn = Gtk.Button(label=f"{prefix}{name}")
        header_btn.get_style_context().add_class("net-btn")
        if is_connected:
            header_btn.get_style_context().add_class("connected")

        details = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        details.get_style_context().add_class("details-box")
        details.set_visible(False)

        status_label = Gtk.Label(label="")
        status_label.set_visible(False)

        if is_connected:
            action_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            disc_btn = Gtk.Button(label="Baglantiyi Kes")
            disc_btn.connect("clicked", lambda w, m=mac, sl=status_label, b=disc_btn: self.start_disconnect(m, sl, b))
            action_row.pack_start(disc_btn, False, False, 0)
            action_row.pack_start(status_label, False, False, 0)
            details.pack_start(action_row, False, False, 0)
        elif is_paired:
            action_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            conn_btn = Gtk.Button(label="Baglan")
            conn_btn.connect("clicked", lambda w, m=mac, sl=status_label, b=conn_btn: self.start_direct_connect(m, sl, b))
            action_row.pack_start(conn_btn, False, False, 0)

            unpair_btn = Gtk.Button(label="Eslesmeyi Sil")
            unpair_btn.connect("clicked", lambda w, m=mac: self.remove_device(m))
            action_row.pack_start(unpair_btn, False, False, 0)

            action_row.pack_start(status_label, False, False, 0)
            details.pack_start(action_row, False, False, 0)
        else:
            # Eşleşmemiş cihaz için PIN kutusu (Telefon kodu için opsiyonel)
            pin_entry = Gtk.Entry()
            pin_entry.set_placeholder_text("PIN / Kod (Gerekirse)")
            pin_entry.get_style_context().add_class("pass-entry")
            details.pack_start(pin_entry, False, False, 0)

            action_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            pair_btn = Gtk.Button(label="Esle ve Baglan")
            pair_btn.connect("clicked", lambda w, m=mac, pe=pin_entry, sl=status_label, b=pair_btn: self.start_pair_and_connect(m, pe, sl, b))
            action_row.pack_start(pair_btn, False, False, 0)
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

    def remove_device(self, mac):
        subprocess.run(["bluetoothctl", "remove", mac], capture_output=True)
        self.finish_rescan()

    def start_direct_connect(self, mac, status_lbl, btn):
        btn.set_sensitive(False)
        status_lbl.set_label("...")
        status_lbl.get_style_context().remove_class("status-ok")
        status_lbl.get_style_context().remove_class("status-err")
        status_lbl.set_visible(True)

        def worker():
            subprocess.run(["bluetoothctl", "trust", mac], capture_output=True)
            subprocess.run(["bluetoothctl", "connect", mac], capture_output=True)
            time.sleep(1)
            chk = subprocess.run(["bluetoothctl", "info", mac], capture_output=True, text=True)
            success = "Connected: yes" in chk.stdout
            GLib.idle_add(self.apply_action_result, success, status_lbl, btn)

        threading.Thread(target=worker, daemon=True).start()

    def start_pair_and_connect(self, mac, pin_entry, status_lbl, btn):
        btn.set_sensitive(False)
        pin_entry.set_sensitive(False)
        status_lbl.set_label("...")
        status_lbl.get_style_context().remove_class("status-ok")
        status_lbl.get_style_context().remove_class("status-err")
        status_lbl.set_visible(True)

        pin = pin_entry.get_text().strip()

        def pair_worker():
            success = False
            try:
                subprocess.run(["bluetoothctl", "trust", mac], capture_output=True)
                
                # Eğer kullanıcı PIN kutusuna şifre yazdıysa bt-agent ile o PIN'i besle
                if pin:
                    cmd = f"echo '{pin}' | bt-agent -c DisplayYesNo -p /dev/stdin & sleep 0.5; bluetoothctl pair {mac}"
                    subprocess.run(cmd, shell=True, capture_output=True, timeout=20)
                else:
                    # PIN girilmediyse standart pair tetikle
                    subprocess.run(["bluetoothctl", "pair", mac], capture_output=True, timeout=20)

                subprocess.run(["bluetoothctl", "trust", mac], capture_output=True)
                subprocess.run(["bluetoothctl", "connect", mac], capture_output=True, timeout=10)

                time.sleep(1)
                chk = subprocess.run(["bluetoothctl", "info", mac], capture_output=True, text=True)
                if "Connected: yes" in chk.stdout or "Paired: yes" in chk.stdout:
                    success = True
            except Exception:
                success = False

            GLib.idle_add(self.apply_pair_result, success, status_lbl, btn, pin_entry)

        threading.Thread(target=pair_worker, daemon=True).start()

    def apply_pair_result(self, success, status_lbl, btn, pin_entry):
        btn.set_sensitive(True)
        pin_entry.set_sensitive(True)
        self.apply_action_result(success, status_lbl, btn)

    def start_disconnect(self, mac, status_lbl, btn):
        btn.set_sensitive(False)
        status_lbl.set_label("...")
        status_lbl.get_style_context().remove_class("status-ok")
        status_lbl.get_style_context().remove_class("status-err")
        status_lbl.set_visible(True)

        def disconnect_worker():
            res = subprocess.run(["bluetoothctl", "disconnect", mac], capture_output=True, text=True)
            success = "Successful disconnected" in res.stdout or res.returncode == 0
            GLib.idle_add(self.apply_action_result, success, status_lbl, btn)

        threading.Thread(target=disconnect_worker, daemon=True).start()

    def apply_action_result(self, success, status_lbl, btn):
        btn.set_sensitive(True)
        if success:
            status_lbl.set_label("[✓]")
            status_lbl.get_style_context().add_class("status-ok")
            GLib.timeout_add(1000, self.finish_rescan)
        else:
            status_lbl.set_label("[✗]")
            status_lbl.get_style_context().add_class("status-err")

if __name__ == "__main__":
    win = BluetoothMenu()
    win.show_all()
    win.move(95, 430)
    Gtk.main()
