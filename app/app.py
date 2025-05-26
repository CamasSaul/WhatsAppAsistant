import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox, QVBoxLayout

class App (QApplication):
    def __init__ (self, debug=False):
        super().__init__()
        ventana = MiVentana()
        ventana.show()
        sys.exit(app.exec_())



class Window (QWidget):
    def __init__(self, parent: typing.Optional['QWidget'] = ..., flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = ...) -> None:
        super().__init__(parent, flags)
        self.setWindowTitle('WhatsApp Autoresponder')
        self.setGeometry(100, 100, 300, 300)

        self.button = QPushButton('Click aquí', self)
        self.button.clicked.connect()

    def show_message (self):
        ...



class MiVentana(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mi Interfaz con PyQt")
        self.setGeometry(100, 100, 300, 200)

        self.boton = QPushButton("Haz clic", self)
        self.boton.clicked.connect(self.mostrar_mensaje)

        layout = QVBoxLayout()
        layout.addWidget(self.boton)
        self.setLayout(layout)

    def mostrar_mensaje(self):
        QMessageBox.information(self, "Mensaje", "¡Hola desde PyQt!")