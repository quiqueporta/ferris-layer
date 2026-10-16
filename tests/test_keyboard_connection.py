from ferris_layer.keyboard_connection import KeyboardConnection


class FinderStub:
    def __init__(self, path):
        self._path = path

    def find(self):
        return self._path


class WatcherSpy:
    def __init__(self):
        self.watched = []

    def watch(self, reports):
        self.watched.extend(reports)


class WaitSpy:
    def __init__(self):
        self.calls = 0

    def __call__(self):
        self.calls += 1


class FakeKeyboard:
    def __init__(self, path, reports):
        self.path = path
        self.events = []
        self._reports = reports

    def request_current_layer(self):
        self.events.append("request")

    def reports(self):
        self.events.append("read")

        yield from self._reports(self.path)

    def close(self):
        self.events.append("close")


def plugged_reports(path):
    yield path.encode()


def unplugged_reports(path):
    yield b"LY\x01"
    raise OSError("No such device")


def connection_with(finder, watcher=None, wait=None, reports=plugged_reports, opened=None):
    def open_keyboard(path):
        keyboard = FakeKeyboard(path, reports)
        if opened is not None:
            opened.append(keyboard)

        return keyboard

    return KeyboardConnection(
        finder=finder,
        open_keyboard=open_keyboard,
        watcher=watcher or WatcherSpy(),
        wait=wait or WaitSpy(),
    )


def test_reads_the_reports_of_the_connected_keyboard():
    watcher = WatcherSpy()
    connection = connection_with(FinderStub("/dev/hidraw2"), watcher=watcher)

    connection.run_once()

    assert watcher.watched == [b"/dev/hidraw2"]


def test_asks_the_keyboard_for_its_current_layer_before_reading():
    opened = []
    connection = connection_with(FinderStub("/dev/hidraw2"), opened=opened)

    connection.run_once()

    assert opened[0].events == ["request", "read", "close"]


def test_waits_when_the_keyboard_is_unplugged():
    wait = WaitSpy()
    connection = connection_with(FinderStub(None), wait=wait)

    connection.run_once()

    assert wait.calls == 1


def test_waits_when_the_keyboard_is_unplugged_while_reading():
    wait = WaitSpy()
    watcher = WatcherSpy()
    connection = connection_with(
        FinderStub("/dev/hidraw2"), watcher=watcher, wait=wait, reports=unplugged_reports
    )

    connection.run_once()

    assert (watcher.watched, wait.calls) == ([b"LY\x01"], 1)
