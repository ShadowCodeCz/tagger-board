import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtChart import QChart, QChartView, QBarSet, QBarSeries, QBarCategoryAxis

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Vytvoření datové sady
        set0 = QBarSet("Produkt A")
        set1 = QBarSet("Produkt B")

        set0 << 1 << 2 << 3 << 4 << 5 << 6
        set1 << 5 << 0 << 0 << 4 << 0 << 7

        # Přidání datových sad do série
        series = QBarSeries()
        series.append(set0)
        series.append(set1)

        # Vytvoření grafu a přidání série
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Jednoduchý sloupcový graf")
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        # Nastavení osy X
        categories = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
        axisX = QBarCategoryAxis()
        axisX.append(categories)
        chart.addAxis(axisX, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axisX)

        # Nastavení zobrazení grafu
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)

        # Vytvoření widgetu pro zobrazení grafu a nastavení jako centrální widget
        chartView = QChartView(chart)
        self.setCentralWidget(chartView)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
