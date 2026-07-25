from __future__ import annotations

import logging
import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from app.core.config import ConfigManager
from app.gui.main_window import MainWindow
from app.utils.logging import configure_logging


def main() -> int:
    configure_logging()
    app = QApplication(sys.argv)
    try:
        window = MainWindow(ConfigManager())
        window.show()
        return app.exec()
    except Exception as exc:
        logging.exception("Fatal application error")
        QMessageBox.critical(None, "DNF Nickname Finder", str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
