import gi

gi.require_version("Gtk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
from gi.repository import GdkPixbuf, GLib, Gtk


SCALE = 0.75
PADDING = 12


class LayoutWindow:
    def __init__(self):
        self._on_close = lambda: None
        self._image = Gtk.Image()
        self._message = Gtk.Label()
        self._window = self._window_with(self._image, self._message)

    def when_closed(self, callback):
        self._on_close = callback

    def show(self, title, svg):
        self._image.set_from_pixbuf(self._pixbuf_of(svg))
        self._window.set_title(title)
        self._message.hide()
        self._image.show()
        self._window.present()

    def show_message(self, text):
        self._message.set_text(text)
        self._window.set_title("Ferris Sweep layout")
        self._image.hide()
        self._message.show()
        self._window.present()

    def _window_with(self, image, message):
        window = Gtk.Window(title="Ferris Sweep layout")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin=PADDING)

        box.pack_start(image, False, False, 0)
        box.pack_start(message, False, False, 0)
        window.add(box)
        window.set_resizable(False)
        window.set_keep_above(True)
        window.connect("delete-event", self._hide)
        box.show()

        return window

    def _hide(self, window, _event):
        window.hide()
        self._on_close()

        return True

    def _pixbuf_of(self, svg):
        loader = GdkPixbuf.PixbufLoader.new_with_type("svg")
        loader.connect("size-prepared", self._scale)
        loader.write(svg.encode())
        loader.close()

        return loader.get_pixbuf()

    def _scale(self, loader, width, height):
        loader.set_size(round(width * SCALE), round(height * SCALE))


class MainLoopDisplay:
    def __init__(self, display):
        self._display = display

    def show(self, layer):
        GLib.idle_add(self._show_once, layer)

    def _show_once(self, layer):
        self._display.show(layer)

        return False
