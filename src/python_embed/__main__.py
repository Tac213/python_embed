# -*- coding: utf-8 -*-
# author: Tac
# contact: cookiezhx@163.com

import sys
from PySide6 import QtWidgets


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    label = QtWidgets.QLabel("Hello World Hey Hey")
    label.show()
    sys.exit(app.exec())
