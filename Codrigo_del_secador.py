import matplotlib.pyplot as plt

def calcular_comportamiento_deshidratador_basico(
    T_ambiente, G, A_colector, eta_colector,
    m_inicial, MC_inicial, MC_final
):
    """
    Simulación básica del deshidratador solar.
    Asume una tasa de secado promedio simplificada.
    """
    # Validaciones básicas
    if not (0 < eta_colector <= 1):
        raise ValueError("La eficiencia del colector debe estar entre 0 y 1.")
    if not (0 < MC_inicial < 1):
        raise ValueError("La humedad inicial debe estar entre 0 y 1.")
    if not (0 < MC_final < 1):
        raise ValueError("La humedad final debe estar entre 0 y 1.")
    if MC_final >= MC_inicial:
        raise ValueError("La humedad final debe ser menor que la inicial.")
    if m_inicial <= 0:
        raise ValueError("La masa inicial debe ser mayor que cero.")
    if A_colector <= 0:
        raise ValueError("El área del colector debe ser mayor que cero.")
    if G <= 0:
        raise ValueError("La radiación solar debe ser mayor que cero.")

    # 1. CÁLCULO DE ENERGÍA
    Q_util = G * A_colector * eta_colector
    Lv = 2.4e6  # J/kg
    m_agua_max = Q_util / Lv

    # 2. CÁLCULO DEL AGUA A ELIMINAR
    m_seco = m_inicial * (1 - MC_inicial)
    m_agua_inicial = m_inicial * MC_inicial
    m_final = m_seco / (1 - MC_final)
    m_agua_final = m_final - m_seco
    m_agua_a_remover = m_agua_inicial - m_agua_final

    # 3. ESTIMACIÓN DEL TIEMPO (SIMPLIFICADA)
    t_segundos = m_agua_a_remover / m_agua_max
    t_horas = t_segundos / 3600

    # 4. RESULTADOS
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
        "MC_final": MC_final
    }
    return resultados

def calcular_curva_secado(resultados, pasos=100):
    """
    Calcula la curva de secado usando los resultados de la simulación básica.
    """
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
        MC = max(MC, MC_final)  # No bajar de la humedad final
        tiempos.append(t / 3600)  # horas
        humedades.append(MC)
    return tiempos, humedades

# --- DATOS DE ENTRADA (modificables por el usuario) ---
datos_entrada = {
    "T_ambiente": 25,    # °C
    "G": 800,            # W/m^2
    "A_colector": 2.0,   # m^2 
    "eta_colector": 0.5, # eficiencia
    "m_inicial": 1.0,    # kg
    "MC_inicial": 0.87,  # humedad inicial
    "MC_final": 0.25     # humedad final
}

# --- EJECUTAR SIMULACIÓN ---
resultados = calcular_comportamiento_deshidratador_basico(**datos_entrada)

print("--- ☀️ Resultados de Simulación Básica ---")
print(f"Energía útil aportada: {resultados['Q_util']} W")
print(f"Masa de sólido seco: {resultados['m_seco']} kg")
print(f"Masa de agua a remover: {resultados['m_agua_a_remover']} kg")
print(f"Tiempo de secado estimado (mínimo teórico): {resultados['t_horas_estimado_minimo']} horas")

# --- CALCULAR Y GRAFICAR CURVA DE SECADO ---
tiempos, humedades = calcular_curva_secado(resultados)

plt.plot(tiempos, humedades)
plt.xlabel("Tiempo (horas)")
plt.ylabel("Humedad (base húmeda)")
plt.title("Curva de secado solar (simplificada)")
plt.grid(True)
plt.show()



