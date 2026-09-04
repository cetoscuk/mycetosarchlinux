#!/usr/bin/env python3
import gi
import subprocess
import os
import json
import threading
import time

gi.require_version("Gtk", "3.0")
gi.require_version("GtkLayerShell", "0.1")
from gi.repository import Gtk, Gdk, GLib
from gi.repository import GtkLayerShell

class MinecraftWorkspaces(Gtk.Window):
    def __init__(self):
        super().__init__()
        
        # Wayland Layer Shell entegrasyonu (Waybar gibi ekrana kenetlenir)
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.TOP)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.LEFT, 8)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.TOP, 10)
        GtkLayerShell.set_exclusive_zone(self, 0)

        # CSS Yükleme
        provider = Gtk.CssProvider()
        css = b"""
        window {
            background: transparent;
        }
        .ws-box {
            background-color: #092328;
            border: 2px solid #2A835F;
            border-radius: 8px;
            padding: 4px;
        }
        .ws-btn {
            background-color: #12544F;
            border: 2px solid #2A835F;
            border-radius: 6px;
            min-width: 44px;
            min-height: 36px;
            margin: 2px 0px;
            box-shadow: none;
            outline: none;
        }
        .ws-btn label {
            color: #8BBB92;
            font-family: "Monocraft", monospace;
            font-size: 14px;
            font-weight: bold;
        }
        .ws-btn:hover {
            background-color: #2A835F;
            border-color: #8BBB92;
        }
        .ws-btn:hover label {
            color: #8BBB92;
        }
        .ws-btn.active {
            background-color: #8BBB92;
            border-color: #8BBB92;
        }
        .ws-btn.active label {
            color: #092328;
        }
        """
        provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        box.get_style_context().add_class("ws-box")
        self.add(box)

        self.buttons = {}
        for i in range(1, 5):
            btn = Gtk.Button(label=str(i))
            btn.get_style_context().add_class("ws-btn")
            btn.connect("clicked", self.on_workspace_clicked, i)
            box.pack_start(btn, False, False, 0)
            self.buttons[i] = btn

        self.update_active_workspace()
        self.connect("destroy", Gtk.main_quit)

        # Arka planda workspace değişimini dinleyen döngü
        threading.Thread(target=self.hyprland_event_listener, daemon=True).start()

    def on_workspace_clicked(self, widget, ws_id):
        # Tıklandığı an direkt Hyprland'e komut ver
        subprocess.run(["hyprctl", "dispatch", "workspace", str(ws_id)])
        self.set_active_ui(ws_id)

    def set_active_ui(self, active_id):
        for ws_id, btn in self.buttons.items():
            if ws_id == active_id:
                btn.get_style_context().add_class("active")
            else:
                btn.get_style_context().remove_class("active")

    def update_active_workspace(self):
        try:
            res = subprocess.run(["hyprctl", "activeworkspace", "-j"], capture_output=True, text=True)
            data = json.loads(res.stdout)
            active_id = data.get("id", 1)
            self.set_active_ui(active_id)
        except Exception:
            pass

    def hyprland_event_listener(self):
        # Hyprland soketini dinle, klavyeyle bile değişse anında rengi güncelle
        his = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
        sock_path = f"/tmp/hypr/{his}/.socket2.sock"
        if not os.path.exists(sock_path):
            sock_path = f"/run/user/{os.getuid()}/hypr/{his}/.socket2.sock"

        while True:
            try:
                import socket
                with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                    s.connect(sock_path)
                    while True:
                        data = s.recv(1024).decode("utf-8")
                        if "workspace>>" in data:
                            GLib.idle_add(self.update_active_workspace)
            except Exception:
                time.sleep(1)

if __name__ == "__main__":
    win = MinecraftWorkspaces()
    win.show_all()
    Gtk.main()
