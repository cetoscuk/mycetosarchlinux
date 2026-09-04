#!/usr/bin/env python3
import sys
import subprocess
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk

def get_volume():
    try:
        out = subprocess.check_output(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"]).decode()
        val = float(out.split()[1])
        return min(int(val * 100), 100)
    except Exception:
        return 50

class AudioSlider(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("mc-audio-popup")
        self.set_default_size(230, 160)
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_keep_above(True)

        # DOĞRUDAN GTK ÜZERİNDEN KOORDİNAT VERME
        self.move(95, 510)

        # CSS Yükleme
        provider = Gtk.CssProvider()
        provider.load_from_path(f"{subprocess.os.path.expanduser('~')}/.config/waybar/mc-audio.css")
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(box)

        # Üst Başlık Satırı
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        
        lbl_dummy = Gtk.Label(label="   ")
        header.pack_start(lbl_dummy, False, False, 0)

        lbl_title = Gtk.Label(label="SES AYARI")
        lbl_title.get_style_context().add_class("title")
        lbl_title.set_hexpand(True)
        lbl_title.set_halign(Gtk.Align.CENTER)
        header.pack_start(lbl_title, True, True, 0)

        btn_x = Gtk.Button(label="✕")
        btn_x.connect("clicked", lambda w: self.close_app())
        header.pack_end(btn_x, False, False, 0)
        box.pack_start(header, False, False, 0)

        # Slider ve Yüzde
        current_vol = get_volume()
        self.lbl_val = Gtk.Label(label=f"%{current_vol}")
        self.lbl_val.set_halign(Gtk.Align.CENTER)
        box.pack_start(self.lbl_val, False, False, 0)

        self.scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.scale.set_value(current_vol)
        self.scale.set_draw_value(False)
        self.scale.connect("value-changed", self.on_slider_move)
        box.pack_start(self.scale, False, False, 0)

        # Butonlar
        btn_mute = Gtk.Button(label="Sesi Sustur / Ac")
        btn_mute.connect("clicked", self.toggle_mute)
        box.pack_start(btn_mute, False, False, 0)

        btn_dev = Gtk.Button(label="Cikis Aygiti Sec")
        btn_dev.connect("clicked", self.select_device)
        box.pack_start(btn_dev, False, False, 0)

        # Pencere ekrana çizildikten hemen sonra tekrar koordinata sabitle
        self.connect("realize", self.on_realize)

    def on_realize(self, widget):
        self.move(95, 510)

    def close_app(self):
        Gtk.main_quit()
        sys.exit(0)

    def on_slider_move(self, widget):
        val = int(widget.get_value())
        self.lbl_val.set_text(f"%{val}")
        subprocess.run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{val}%"])

    def toggle_mute(self, widget):
        subprocess.run(["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"])

    def select_device(self, widget):
        cmd = """
        sleep 0.1
        SINKS=$(wpctl status | sed -n '/Sinks:/,/Sources:/p' | grep -E '│.*[0-9]+\\.' | sed 's/│//g; s/^[ \\t]*//')
        DEVICE=$(echo "$SINKS" | rofi -dmenu -p "Aygit:" -theme ~/.config/waybar/audio-card.rasi)
        if [ -n "$DEVICE" ]; then
            ID=$(echo "$DEVICE" | grep -oP '(?<=[* ])[0-9]+(?=\\.)')
            [ -z "$ID" ] && ID=$(echo "$DEVICE" | awk '{print $1}' | tr -d '.')
            wpctl set-default "$ID"
        fi
        """
        subprocess.Popen(cmd, shell=True)
        self.close_app()

if __name__ == "__main__":
    win = AudioSlider()
    win.show_all()
    # Pencere çizildikten hemen sonra koordinata zorla
    win.move(95, 510)
    Gtk.main()
