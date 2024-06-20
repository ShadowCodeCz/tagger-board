import sys
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QBrush, QColor, QFont
from PyQt6.QtCore import Qt, QRectF

class BarChartWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sloupcový Graf v PyQt6")
        self.setGeometry(100, 100, 400, 300)
        self.data = {"Červená": 30, "Zelená": 15, "Modrá": 45, "Žlutá": 10}
        self.colors = ["red", "green", "blue", "yellow"]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setFont(QFont("Arial", 10))

        max_value = max(self.data.values())
        bar_width = self.width() / (len(self.data) + 1)
        for i, (category, value) in enumerate(self.data.items()):
            color = self.colors[i % len(self.colors)]
            bar_height = (value / max_value) * (self.height() - 20)  # Výpočet výšky sloupce
            x = (i + 1) * bar_width
            y = self.height() - bar_height - 10  # 10 pixelů od dolního okraje pro popisky
            painter.setBrush(QBrush(QColor(color)))
            painter.drawRect(x, y, bar_width - 5, bar_height)  # 5 pixelů mezera mezi sloupci

            # Vykreslení popisku nad sloupec
            text = f"{category}: {value}"
            painter.drawText(x + (bar_width - 5) / 2 - painter.fontMetrics().width(text) / 2, y - 5, text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = BarChartWidget()
    demo.show()
    sys.exit(app.exec())
