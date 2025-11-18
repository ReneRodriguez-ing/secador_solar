#INTERFAZ DE USUARIO CON PyQt5
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QLineEdit, QPushButton
import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

def calcular_comportamiento_deshidratador_basico(
    T_ambiente, G, A_colector, eta_colector,
    m_inicial, MC_inicial, MC_final
):
    Lv = 2.4e6  # J/kg
    Q_util = G * A_colector * eta_colector
    m_agua_max = Q_util / Lv
    m_seco = m_inicial * (1 - MC_inicial)
    m_agua_inicial = m_inicial * MC_inicial
    m_final = m_seco / (1 - MC_final)
    m_agua_final = m_final - m_seco
    m_agua_a_remover = m_agua_inicial - m_agua_final
    t_segundos = m_agua_a_remover / m_agua_max
    t_horas = t_segundos / 3600
    resultados = {
        "Q_util": round(Q_util, 2),
        "m_seco": round(m_seco, 3),
        "m_agua_a_remover": round(m_agua_a_remover, 3),
        "t_horas_estimado_minimo": round(t_horas, 2),
        "m_agua_inicial": m_agua_inicial,
        "m_agua_final": m_agua_final,
        "m_seco_val": m_seco,
        "m_agua_max": m_agua_max,
        "t_total_seg": t_segundos,
        "MC_inicial": MC_inicial,
        "MC_final": MC_final,
        "m_final": m_final
    }
    return resultados

def calcular_curva_secado(resultados, pasos=100):
    m_agua_inicial = resultados["m_agua_inicial"]
    m_agua_final = resultados["m_agua_final"]
    m_seco = resultados["m_seco_val"]
    m_agua_max = resultados["m_agua_max"]
    t_total = resultados["t_total_seg"]
    MC_final = resultados["MC_final"]
    tiempos = []
    humedades = []
    for i in range(pasos + 1):
        t = t_total * i / pasos
        m_agua = max(m_agua_inicial - m_agua_max * t, m_agua_final)
        MC = m_agua / (m_seco + m_agua)
        MC = max(MC, MC_final)
        tiempos.append(t / 3600)
        humedades.append(MC)
    return tiempos, humedades

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulación de Deshidratador Solar")

        # Crear widgets
        self.layout = QVBoxLayout()

        self.label_temp = QLabel("Temperatura ambiente (°C):")
        self.input_temp = QLineEdit("25")
        self.layout.addWidget(self.label_temp)
        self.layout.addWidget(self.input_temp)

        self.label_radiacion = QLabel("Radiación solar (W/m²):")
        self.input_radiacion = QLineEdit("800")
        self.layout.addWidget(self.label_radiacion)
        self.layout.addWidget(self.input_radiacion)

        self.label_area = QLabel("Área del colector (m²):")
        self.input_area = QLineEdit("2.0")
        self.layout.addWidget(self.label_area)
        self.layout.addWidget(self.input_area)

        self.label_eficiencia = QLabel("Eficiencia del colector (0-1):")
        self.input_eficiencia = QLineEdit("0.5")
        self.layout.addWidget(self.label_eficiencia)
        self.layout.addWidget(self.input_eficiencia)

        self.label_peso = QLabel("Peso inicial (kg):")
        self.input_peso = QLineEdit("1.0")
        self.layout.addWidget(self.label_peso)
        self.layout.addWidget(self.input_peso)

        self.label_humedad_inicial = QLabel("Humedad inicial (0-1):")
        self.input_humedad_inicial = QLineEdit("0.87")
        self.layout.addWidget(self.label_humedad_inicial)
        self.layout.addWidget(self.input_humedad_inicial)

        self.label_humedad_final = QLabel("Humedad final (0-1):")
        self.input_humedad_final = QLineEdit("0.25")
        self.layout.addWidget(self.label_humedad_final)
        self.layout.addWidget(self.input_humedad_final)

        self.button_calcular = QPushButton("Calcular")
        self.button_calcular.clicked.connect(self.calcular)
        self.layout.addWidget(self.button_calcular)

        self.result_label = QLabel("Resultados:")
        self.layout.addWidget(self.result_label)

        self.canvas = FigureCanvas(plt.figure())
        self.layout.addWidget(self.canvas)

        # Configurar el widget principal
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def calcular(self):
        # Obtener valores de entrada
        T_ambiente = float(self.input_temp.text())
        G = float(self.input_radiacion.text())
        A_colector = float(self.input_area.text())
        eta_colector = float(self.input_eficiencia.text())
        m_inicial = float(self.input_peso.text())
        MC_inicial = float(self.input_humedad_inicial.text())
        MC_final = float(self.input_humedad_final.text())

        # Calcular resultados
        resultados = calcular_comportamiento_deshidratador_basico(
            T_ambiente, G, A_colector, eta_colector, m_inicial, MC_inicial, MC_final
        )

        # Mostrar resultados
        horas = int(resultados['t_horas_estimado_minimo'])
        minutos = int((resultados['t_horas_estimado_minimo'] - horas) * 60)
        self.result_label.setText(
            f"Peso final teórico: {round(resultados['m_final'], 3)} kg\n"
            f"Energía útil aportada: {resultados['Q_util']} W\n"
            f"Masa de sólido seco: {resultados['m_seco']} kg\n"
            f"Masa de agua a remover: {resultados['m_agua_a_remover']} kg\n"
            f"Tiempo de secado estimado: {horas} horas y {minutos} minutos"
        )

        # Graficar curva de secado
        tiempos, humedades = calcular_curva_secado(resultados)
        self.canvas.figure.clear()
        ax = self.canvas.figure.add_subplot(111)
        ax.plot(tiempos, humedades, label="Curva de secado")
        ax.set_xlabel("Tiempo (horas)")
        ax.set_ylabel("Humedad (base húmeda)")
        ax.set_title("Curva de secado solar")
        ax.grid(True)
        ax.legend()
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())