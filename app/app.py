import sys
from PyQt5.QtWidgets import QApplication, QLabel, QLayout, QWidget, QPushButton, QMessageBox, QVBoxLayout

class BotonPersonalizado(QPushButton):
    def __init__(self, texto, parent):
        super().__init__(texto, parent)
        self.setStyleSheet("background-color: green; color: white; font-weight: bold;")

class Window (QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle('WhatsApp Autoresponder')
        self.setGeometry(100, 100, 300, 300)

        self.button = BotonPersonalizado('Click aquí', self)
        self.button.clicked.connect(self.show_message)

        layout = QVBoxLayout()
        layout.addChildWidget(self.button)
        self.setLayout(layout)

    def show_message (self):
        QMessageBox.information(self, 'Mensaje', 'Botón presionado.')


app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec_())