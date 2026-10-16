REPORT_SIZE = 32
NO_REPORT_ID = b"\x00"
CHUNK_SIZE = REPORT_SIZE - 4

GET_LAYER_COUNT = 0x11
GET_KEYMAP_BUFFER = 0x12
SET_KEYMAP_BUFFER = 0x13
GET_MACRO_BUFFER_SIZE = 0x0D
GET_MACRO_BUFFER = 0x0E
SET_MACRO_BUFFER = 0x0F


class ViaProtocol:
    def __init__(self, keyboard):
        self._keyboard = keyboard

    def layer_count(self):
        return self._request(bytes([GET_LAYER_COUNT]))[1]

    def macro_buffer_size(self):
        return int.from_bytes(self._request(bytes([GET_MACRO_BUFFER_SIZE]))[1:3], "big")

    def read_keymap(self, size):
        return self._read_buffer(GET_KEYMAP_BUFFER, size)

    def read_macros(self, size):
        return self._read_buffer(GET_MACRO_BUFFER, size)

    def write_keymap(self, data):
        self._write_buffer(SET_KEYMAP_BUFFER, data)

    def write_macros(self, data):
        self._write_buffer(SET_MACRO_BUFFER, data)

    def _read_buffer(self, command_id, size):
        data = bytearray()
        for offset in range(0, size, CHUNK_SIZE):
            chunk_size = min(CHUNK_SIZE, size - offset)
            response = self._request(self._buffer_header(command_id, offset, chunk_size))
            data += response[4:4 + chunk_size]

        return bytes(data)

    def _write_buffer(self, command_id, data):
        for offset in range(0, len(data), CHUNK_SIZE):
            chunk = data[offset:offset + CHUNK_SIZE]
            self._request(self._buffer_header(command_id, offset, len(chunk)) + chunk)

    def _buffer_header(self, command_id, offset, size):
        return bytes([command_id]) + offset.to_bytes(2, "big") + bytes([size])

    def _request(self, command):
        self._keyboard.write(NO_REPORT_ID + command.ljust(REPORT_SIZE, b"\x00"))

        return self._response_to(command[0])

    def _response_to(self, command_id):
        while True:
            response = self._keyboard.read()
            if response[0] == command_id:
                return response
