from ferris_layer.backup_drawings import BackupDrawings


class LayerImages:
    def __init__(self, rows, cols, directory):
        self._drawings = BackupDrawings(rows, cols)
        self._directory = directory

    def write(self, backup):
        self._directory.mkdir(parents=True, exist_ok=True)

        for number, svg in enumerate(self._drawings.svgs(backup)):
            (self._directory / f"layer-{number}.svg").write_text(svg)
