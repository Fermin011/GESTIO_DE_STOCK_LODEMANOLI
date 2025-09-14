from PyQt6.QtGui import QPalette, QColor

def apply_theme(app, theme="dark"):
    palette = QPalette()

    if theme == "dark":
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(142, 45, 197))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))

    else:  # light theme
        palette.setColor(QPalette.ColorRole.Window, QColor(239, 240, 241))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(239, 240, 241))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 220))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Button, QColor(239, 240, 241))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(61, 174, 233))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))

    app.setPalette(palette)

    # 🔹 Estilos por defecto
    app.setStyleSheet("""
        /* Quitamos la transparencia global para no afectar botones */
        QWidget {
            font-family: Arial, sans-serif;
        }

        /* Si querés contenedores transparentes, usá este objeto */
        QWidget#transparentContainer {
            background: transparent;
        }

        QLabel {
            font-size: 14px;
        }

        QPushButton {
            background-color: #367B94;
            color: white;
            border: 1px solid #1B4F63;
            border-radius: 12px;
            padding: 10px;
            font-size: 12pt;
            font-weight: 600;
        }
        QPushButton:hover {
            background-color: #3f8daa;
        }
        QPushButton:pressed {
            background-color: #2b5f74;
        }
    """)
