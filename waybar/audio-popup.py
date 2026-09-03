#!/usr/bin/env python3
import subprocess
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk, GLib

def get_volume():
    try:
        out = subprocess.check_output(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"]).decode()
        val = float(out.split()[1])
        return min(int(val * 100), 100)
    except Exception:
        return 50

def get_device():
    try:
        out = subprocess.check_output(["wpctl", "status"]).decode()
        for line in out.splitlines():
            if "*" in line and "vol:" in line.lower():
                clean = line.replace("*", "").replace("│", "").strip()
                name = clean.split(".")[1].split("[")[0].strip()
                return name[:22]
    except Exception:
        pass
    return "Hoparlör"

class AudioPopup(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("AudioPopup")
        self.set_wmclass("mc-audio-popup", "mc-audio-popup")
        self.set_role("mc-audio-popup")
        self.set_type_hint(Gdk.WindowTypeHint.UTILITY)
        self.set_default_size(250, 240)
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_skip_taskbar_hint(True)
        self.set_keep_above(True)

        provider = Gtk.CssProvider()
        provider.load_from_path(f"{subprocess.os.path.expanduser('~')}/.config/waybar/audio-popup.css")
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.add(box)

        # Üst Başlık Satırı
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        
        lbl_dummy = Gtk.Label(label="   ")
        header_box.pack_start(lbl_dummy, False, False, 0)

        lbl_title = Gtk.Label(label="SES KONTROLÜ")
        lbl_title.get_style_context().add_class("title")
        lbl_title.set_hexpand(True)
        lbl_title.set_halign(Gtk.Align.CENTER)
        header_box.pack_start(lbl_title, True, True, 0)

        btn_close = Gtk.Button(label="✕")
        btn_close.get_style_context().add_class("btn-close")
        btn_close.connect("clicked", lambda w: Gtk.main_quit())
        header_box.pack_end(btn_close, False, False, 0)

        box.pack_start(header_box, False, False, 0)

        # Cihaz Adı
        self.lbl_device = Gtk.Label(label=get_device())
        self.lbl_device.get_style_context().add_class("device-name")
        self.lbl_device.set_halign(Gtk.Align.CENTER)
        box.pack_start(self.lbl_device, False, False, 0)

        box.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 0)

        # Slider ve Yüzde
        current_vol = get_volume()
        self.lbl_vol = Gtk.Label(label=f"Düzey: %{current_vol}")
        self.lbl_vol.set_halign(Gtk.Align.CENTER)
        box.pack_start(self.lbl_vol, False, False, 2)

        self.scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.scale.set_value(current_vol)
        self.scale.set_draw_value(False)
        self.scale.connect("value-changed", self.on_scale_moved)
        box.pack_start(self.scale, False, False, 0)

        box.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 0)

        # Butonlar
        btn_mute = Gtk.Button(label="Sesi Sustur / Aç")
        btn_mute.connect("clicked", self.toggle_mute)
        box.pack_start(btn_mute, False, False, 2)

        box.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 0)

        btn_switch = Gtk.Button(label="Çıkış Aygıtı Değiştir")
        btn_switch.connect("clicked", self.change_sink)
        box.pack_start(btn_switch, False, False, 2)

        # Firefox veya başka pencereye tıklandığı an kapanma
        self.connect("focus-out-event", lambda w, e: Gtk.main_quit())

    def on_scale_moved(self, widget):
        val = int(widget.get_value())
        self.lbl_vol.set_text(f"Düzey: %{val}")
        subprocess.run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{val}%"])

    def toggle_mute(self, widget):
        subprocess.run(["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"])
        Gtk.main_quit()

    def change_sink(self, widget):
        Gtk.main_quit()
        cmd = """
        SINKS=$(wpctl status | sed -n '/Sinks:/,/Sources:/p' | grep -E '│.*[0-9]+\\.' | sed 's/│//g; s/^[ \\t]*//')
        DEVICE=$(echo "$SINKS" | rofi -dmenu -p "Cihaz:" -theme-str 'window {width: 320px; border: 2px; border-color: #2A835F; background-color: #092328; font: "Monocraft 11";} element {padding: 8px; text-color: #8BBB92;} element selected {background-color: #2A835F; text-color: #092328;}')
        if [ -n "$DEVICE" ]; then
            ID=$(echo "$DEVICE" | grep -oP '(?<=[* ])[0-9]+(?=\\.)')
            [ -z "$ID" ] && ID=$(echo "$DEVICE" | awk '{print $1}' | tr -d '.')
            wpctl set-default "$ID"
        fi
        """
        subprocess.run(cmd, shell=True)

if __name__ == "__main__":
    win = AudioPopup()
    win.show_all()
    Gtk.main()
