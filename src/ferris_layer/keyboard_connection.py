class KeyboardConnection:
    def __init__(self, finder, open_keyboard, watcher, wait):
        self._finder = finder
        self._open_keyboard = open_keyboard
        self._watcher = watcher
        self._wait = wait

    def run_once(self):
        path = self._finder.find()
        if path is None:
            self._wait()
            return

        self._watch_until_unplugged(path)

    def _watch_until_unplugged(self, path):
        try:
            self._watch(self._open_keyboard(path))
        except OSError:
            self._wait()

    def _watch(self, keyboard):
        try:
            keyboard.request_current_layer()
            self._watcher.watch(keyboard.reports())
        finally:
            keyboard.close()
