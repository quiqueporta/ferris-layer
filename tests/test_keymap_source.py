from ferris_layer.keymap_source import KeymapSource


def backup_with(codes, layers):
    keymap = b"".join(code.to_bytes(2, "big") for code in codes)

    return {"layers": layers, "keymap": keymap.hex(), "macros": ""}


def test_renders_each_layer_in_matrix_order():
    backup = backup_with([0x14, 0x1A, 0x04, 0x16, 0x5202, 0x00, 0x412C, 0x01], layers=2)

    source = KeymapSource(rows=2, cols=2).render(backup)

    assert (
        "    [0] = {\n"
        "        { 0x0014, 0x001A },\n"
        "        { 0x0004, 0x0016 },\n"
        "    },\n"
        "    [1] = {\n"
        "        { 0x5202, 0x0000 },\n"
        "        { 0x412C, 0x0001 },\n"
        "    },\n"
    ) in source


def test_hooks_the_layer_report_into_qmk_and_via():
    source = KeymapSource(rows=1, cols=1).render(backup_with([0x14], layers=1))

    assert (
        "layer_report_announce(state);" in source,
        "return layer_report_answer(data);" in source,
    ) == (True, True)
