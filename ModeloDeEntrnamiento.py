"""
Script para entrenar el modelo de Regresión Lineal Simple
Descripción: Entrena un modelo de regresión lineal para predecir salarios basados en años de experiencia
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import json
import os

def entrenar_modelo():
    """
    Función principal que entrena el modelo y guarda los resultados
    """
    print("=" * 60)
    print("ENTRENAMIENTO DEL MODELO DE REGRESIÓN LINEAL SIMPLE")
    print("=" * 60)
    
    # 1. Cargar datos
    print("\n[1] Cargando dataset SalaryData.csv...")
    data_salary = pd.read_csv('SalaryData.csv')
    print(f"✓ Dataset cargado: {len(data_salary)} registros")
    print(f"  Columnas: {list(data_salary.columns)}")
    
    # 2. Extraer características y variable objetivo
    print("\n[2] Extrayendo características (X) y variable objetivo (y)...")
    X = data_salary.iloc[:, :-1].values  # Años de experiencia
    y = data_salary.iloc[:, 1].values    # Salario
    print(f"✓ X (YearsExperience): shape {X.shape}")
    print(f"✓ y (Salary): shape {y.shape}")
    
    # 3. Dividir datos en entrenamiento y prueba
    print("\n[3] Dividiendo datos en conjunto de entrenamiento y prueba...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"✓ Entrenamiento: {len(X_train)} muestras ({80}%)")
    print(f"✓ Prueba: {len(X_test)} muestras ({20}%)")
    
    # 4. Entrenar modelo
    print("\n[4] Entrenando modelo de Regresión Lineal...")
    modelo = LinearRegression()
    modelo.fit(X_train, y_train)
    print("✓ Modelo entrenado exitosamente")
    print(f"  Coeficiente (pendiente): {modelo.coef_[0]:.2f}")
    print(f"  Intercepto: {modelo.intercept_:.2f}")
    
    # 5. Realizar predicciones
    print("\n[5] Realizando predicciones...")
    y_pred_train = modelo.predict(X_train)
    y_pred_test = modelo.predict(X_test)
    print("✓ Predicciones completadas")
    
    # 6. Calcular métricas de evaluación
    print("\n[6] Calculando métricas de evaluación...")
    mae = mean_absolute_error(y_test, y_pred_test)
    mse = mean_squared_error(y_test, y_pred_test)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred_test)
    
    print("\n" + "=" * 60)
    print("MÉTRICAS DE EVALUACIÓN DEL MODELO")
    print("=" * 60)
    print(f"MAE  (Error Absoluto Medio):            ${mae:,.2f}")
    print(f"MSE  (Error Cuadrático Medio):          ${mse:,.2f}")
    print(f"RMSE (Raíz del Error Cuadrático Medio): ${rmse:,.2f}")
    print(f"R² Score (Coeficiente de Determinación): {r2:.4f} ({r2*100:.2f}%)")
    print("=" * 60)
    
    # 7. Guardar el modelo
    print("\n[7] Guardando modelo entrenado...")
    if not os.path.exists('modelo'):
        os.makedirs('modelo')
    
    joblib.dump(modelo, 'modelo/modelo_salario.pkl')
    print("✓ Modelo guardado en: modelo/modelo_salario.pkl")
    
    # 8. Guardar métricas
    print("\n[8] Guardando métricas del modelo...")
    metricas = {
        'mae': float(mae),
        'mse': float(mse),
        'rmse': float(rmse),
        'r2_score': float(r2),
        'coeficiente': float(modelo.coef_[0]),
        'intercepto': float(modelo.intercept_),
        'total_muestras': int(len(data_salary)),
        'muestras_entrenamiento': int(len(X_train)),
        'muestras_prueba': int(len(X_test))
    }
    
    with open('modelo/metricas.json', 'w', encoding='utf-8') as f:
        json.dump(metricas, f, indent=4)
    print("✓ Métricas guardadas en: modelo/metricas.json")
    
    # 9. Generar y guardar gráfica de entrenamiento
    print("\n[9] Generando gráfica del modelo...")
    plt.figure(figsize=(10, 6))
    plt.scatter(X_train, y_train, color='#5B7C99', alpha=0.6, s=80, label='Datos de Entrenamiento', edgecolors='#2C3E50')
    plt.scatter(X_test, y_test, color='#7FA3C9', alpha=0.6, s=80, label='Datos de Prueba', edgecolors='#34495E')
    
    # Línea de regresión
    X_line = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
    y_line = modelo.predict(X_line)
    plt.plot(X_line, y_line, color='#E74C3C', linewidth=3, label='Línea de Regresión')
    
    plt.xlabel('Años de Experiencia', fontsize=12, fontweight='bold')
    plt.ylabel('Salario ($)', fontsize=12, fontweight='bold')
    plt.title('Modelo de Regresión Lineal: Salario vs Años de Experiencia', fontsize=14, fontweight='bold')
    plt.legend(loc='upper left', fontsize=10)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()
    
    if not os.path.exists('static'):
        os.makedirs('static')
    plt.savefig('static/modelo_grafica.png', dpi=150, bbox_inches='tight')
    print("✓ Gráfica guardada en: static/modelo_grafica.png")
    plt.close()
    
    # 10. Guardar datos para la web
    print("\n[10] Preparando datos para la aplicación web...")
    datos_web = {
        'X_train': X_train.flatten().tolist(),
        'y_train': y_train.tolist(),
        'X_test': X_test.flatten().tolist(),
        'y_test': y_test.tolist(),
        'X_all': X.flatten().tolist(),
        'y_all': y.tolist()
    }
    
    with open('modelo/datos_entrenamiento.json', 'w', encoding='utf-8') as f:
        json.dump(datos_web, f, indent=4)
    print("✓ Datos guardados en: modelo/datos_entrenamiento.json")
    
    # 11. Probar el modelo con ejemplos
    print("\n[11] Probando el modelo con valores de ejemplo...")
    print("\n" + "-" * 60)
    print("PREDICCIONES DE EJEMPLO")
    print("-" * 60)
    
    valores_ejemplo = [1, 3, 5, 8, 10, 12, 15]
    for valor in valores_ejemplo:
        prediccion = modelo.predict([[valor]])[0]
        print(f"  Años de Experiencia: {valor:2d} → Salario Predicho: ${prediccion:,.2f}")
    print("-" * 60)
    
    print("\n" + "=" * 60)
    print("¡ENTRENAMIENTO COMPLETADO EXITOSAMENTE!")
    print("=" * 60)
    print("\nArchivos generados:")
    print("  → modelo/modelo_salario.pkl")
    print("  → modelo/metricas.json")
    print("  → modelo/datos_entrenamiento.json")
    print("  → static/modelo_grafica.png")
    print("\n¡El modelo está listo para ser usado en la aplicación web!")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    entrenar_modelo()
