#!/usr/bin/env python3
import subprocess
import json
import re
import os
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf

class NotifWindow(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("Bildirim Merkezi")
        self.set_default_size(460, 520)
        self.set_position(Gtk.WindowPosition.CENTER)
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

        #clear-btn {
            background-image: none;
            background-color: #1e1e2e;
            border: 1px solid #313244;
            color: #cdd6f4;
            padding: 2px 10px;
            border-radius: 6px;
        }
        #clear-btn:hover {
            background-image: -gtk-gradient(linear, left top, right top, from(rgba(110, 50, 140, 0.6)), to(rgba(166, 227, 161, 0.4)));
            border-color: #a6e3a1;
            color: #ffffff;
        }

        list {
            background-color: transparent;
        }
        row {
            padding: 4px 6px;
            border-bottom: 1px solid #181825;
            background-color: transparent;
        }
        row:hover {
            background-color: transparent;
        }

        .notif-btn {
            background-image: none;
            background-color: transparent;
            border: none;
            padding: 6px;
        }
        .notif-btn:hover {
            background-image: -gtk-gradient(linear, left top, right top, from(rgba(110, 50, 140, 0.5)), to(rgba(166, 227, 161, 0.3)));
            border-left: 3px solid #a6e3a1;
            border-radius: 6px;
        }

        #row-del-btn {
            background-image: none;
            background-color: transparent;
            color: #f38ba8;
            font-size: 13px;
            padding: 2px 8px;
            border-radius: 4px;
            border: 1px solid transparent;
        }
        #row-del-btn:hover {
            background-image: -gtk-gradient(linear, left top, right top, from(rgba(243, 139, 168, 0.35)), to(rgba(235, 60, 100, 0.55)));
            border-color: #f38ba8;
            color: #ffffff;
        }

        .app-title {
            color: #a6e3a1;
            font-weight: bold;
        }
        .notif-icon {
            margin-right: 8px;
        }
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css.encode("utf-8"))
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.icon_theme = Gtk.IconTheme.get_default()

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(box)

        # Üst Başlık
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        header.set_name("header")
        box.pack_start(header, False, False, 0)

        title = Gtk.Label(label="⛏️ Bildirim Geçmişi")
        header.pack_start(title, False, False, 0)

        clear_btn = Gtk.Button(label="Tümünü Temizle")
        clear_btn.set_name("clear-btn")
        clear_btn.connect("clicked", self.clear_all_history)
        header.pack_end(clear_btn, False, False, 4)

        close_btn = Gtk.Button(label="✕")
        close_btn.set_name("close-btn")
        close_btn.connect("clicked", lambda w: Gtk.main_quit())
        header.pack_end(close_btn, False, False, 0)

        # Bildirim Listesi
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        box.pack_start(scroll, True, True, 0)

        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scroll.add(self.listbox)

        self.load_notifications()

    def get_app_icon(self, icon_name, app_name):
        size = 32
        # 1. Doğrudan dosya yoluysa
        if icon_name and os.path.exists(icon_name):
            try:
                pix = GdkPixbuf.Pixbuf.new_from_file_at_scale(icon_name, size, size, True)
                return Gtk.Image.new_from_pixbuf(pix)
            except Exception:
                pass

        # 2. İkon temasında ikon adı veya uygulama adını ara
        for name in [icon_name, app_name.lower(), app_name, "dialog-information"]:
            if name and self.icon_theme.has_icon(name):
                try:
                    pix = self.icon_theme.load_icon(name, size, Gtk.IconLookupFlags.FORCE_SIZE)
                    return Gtk.Image.new_from_pixbuf(pix)
                except Exception:
                    pass

        # 3. Bulunamazsa varsayılan bildirim ikonu
        return Gtk.Image.new_from_icon_name("dialog-information", Gtk.IconSize.DND)

    def on_window_clicked(self, widget, event):
        alloc = self.get_allocation()
        if not (0 <= event.x <= alloc.width and 0 <= event.y <= alloc.height):
            Gtk.main_quit()
        return False

    def load_notifications(self):
        try:
            out = subprocess.check_output(["dunstctl", "history"]).decode("utf-8")
            items = json.loads(out).get("data", [[]])[0]
        except Exception:
            items = []

        if not items:
            row = Gtk.ListBoxRow()
            lbl = Gtk.Label(label="Geçmiş bildirim bulunmuyor.")
            lbl.set_margin_top(12)
            lbl.set_margin_bottom(12)
            row.add(lbl)
            self.listbox.add(row)
            return

        for item in items:
            notif_id = item.get("id", {}).get("data")
            app = item.get("appname", {}).get("data", "Sistem")
            summary = item.get("summary", {}).get("data", "")
            body = item.get("body", {}).get("data", "").replace("\n", " ")
            icon_path = item.get("icon_path", {}).get("data", "")

            full_text = f"{summary} {body}"
            urls = re.findall(r"https?://[^\s]+", full_text)
            target_url = urls[0] if urls else None

            row = Gtk.ListBoxRow()
            row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

            # Sol Tıklanabilir İçerik
            content_btn = Gtk.Button()
            content_btn.get_style_context().add_class("notif-btn")
            content_btn.set_relief(Gtk.ReliefStyle.NONE)
            content_btn.connect("clicked", self.trigger_action, target_url, notif_id)

            # İkon ve Metin İçeren Yatay Kutu
            item_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

            # Logo / İkon
            icon_img = self.get_app_icon(icon_path, app)
            icon_img.get_style_context().add_class("notif-icon")
            item_box.pack_start(icon_img, False, False, 0)

            # Başlık ve Açıklama İçeren Dikey Kutu
            text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)

            app_lbl = Gtk.Label(label=f"[{app}] {summary}")
            app_lbl.get_style_context().add_class("app-title")
            app_lbl.set_xalign(0)
            text_box.pack_start(app_lbl, False, False, 0)

            if body:
                body_lbl = Gtk.Label(label=body)
                body_lbl.set_line_wrap(True)
                body_lbl.set_xalign(0)
                text_box.pack_start(body_lbl, False, False, 0)

            item_box.pack_start(text_box, True, True, 0)
            content_btn.add(item_box)
            row_box.pack_start(content_btn, True, True, 0)

            # Sağdaki Tekli Silme Butonu
            del_btn = Gtk.Button(label="✕")
            del_btn.set_name("row-del-btn")
            del_btn.set_relief(Gtk.ReliefStyle.NONE)
            del_btn.connect("clicked", self.delete_single_notif, notif_id, row)
            row_box.pack_end(del_btn, False, False, 2)

            row.add(row_box)
            self.listbox.add(row)

    def delete_single_notif(self, widget, notif_id, row):
        if notif_id:
            subprocess.run(["dunstctl", "history-rm", str(notif_id)])
        self.listbox.remove(row)
        self.listbox.show_all()

    def clear_all_history(self, widget):
        subprocess.run(["dunstctl", "history-clear"])
        Gtk.main_quit()

    def trigger_action(self, widget, url, notif_id):
        if url:
            subprocess.Popen(["xdg-open", url])
        elif notif_id:
            subprocess.run(["dunstctl", "action", str(notif_id)], stderr=subprocess.DEVNULL)
        Gtk.main_quit()

win = NotifWindow()
win.show_all()

display = Gdk.Display.get_default()
seat = display.get_default_seat()
seat.grab(win.get_window(), Gdk.SeatCapabilities.ALL, True, None, None, None)

Gtk.main()
