"""
Aplicación Web Flask para el Modelo de Regresión Lineal Simple
Autor: Proyecto de Extracción de Conocimiento
Descripción: API y servidor web para interactuar con el modelo de predicción de salarios
"""

from flask import Flask, render_template, request, jsonify
import joblib
import json
import os
import numpy as np

app = Flask(__name__)

# Cargar el modelo y las métricas al iniciar la aplicación
MODELO_PATH = 'modelo/modelo_salario.pkl'
METRICAS_PATH = 'modelo/metricas.json'
DATOS_PATH = 'modelo/datos_entrenamiento.json'

def cargar_modelo():
    """Carga el modelo entrenado"""
    if os.path.exists(MODELO_PATH):
        return joblib.load(MODELO_PATH)
    return None

def cargar_metricas():
    """Carga las métricas del modelo"""
    if os.path.exists(METRICAS_PATH):
        with open(METRICAS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def cargar_datos():
    """Carga los datos de entrenamiento"""
    if os.path.exists(DATOS_PATH):
        with open(DATOS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# Cargar recursos al inicio
modelo = cargar_modelo()
metricas = cargar_metricas()
datos = cargar_datos()

@app.route('/')
def index():
    """
    Ruta principal que muestra la página web con información del modelo
    """
    modelo_disponible = modelo is not None
    
    return render_template('index.html', 
                         modelo_disponible=modelo_disponible,
                         metricas=metricas,
                         datos=datos)

@app.route('/api/predecir', methods=['POST'])
def predecir():
    """
    API endpoint para realizar predicciones
    Recibe: JSON con 'anos_experiencia'
    Retorna: JSON con la predicción del salario
    """
    try:
        if modelo is None:
            return jsonify({
                'error': 'El modelo no está disponible. Por favor, entrena el modelo primero.'
            }), 500
        
        # Obtener datos del request
        data = request.get_json()
        anos_experiencia = float(data.get('anos_experiencia', 0))
        
        # Validar entrada
        if anos_experiencia < 0:
            return jsonify({
                'error': 'Los años de experiencia no pueden ser negativos.'
            }), 400
        
        if anos_experiencia > 50:
            return jsonify({
                'error': 'Por favor ingresa un valor realista (0-50 años).'
            }), 400
        
        # Realizar predicción
        prediccion = modelo.predict([[anos_experiencia]])[0]
        
        # Calcular información adicional
        coeficiente = metricas.get('coeficiente', 0)
        intercepto = metricas.get('intercepto', 0)
        
        return jsonify({
            'anos_experiencia': anos_experiencia,
            'salario_predicho': round(prediccion, 2),
            'salario_formateado': f'${prediccion:,.2f}',
            'ecuacion': f'Salario = {intercepto:.2f} + {coeficiente:.2f} × Años',
            'exito': True
        })
    
    except ValueError as e:
        return jsonify({
            'error': 'Entrada inválida. Por favor ingresa un número válido.'
        }), 400
    
    except Exception as e:
        return jsonify({
            'error': f'Error al realizar la predicción: {str(e)}'
        }), 500

@app.route('/api/metricas', methods=['GET'])
def obtener_metricas():
    """
    API endpoint para obtener las métricas del modelo
    Retorna: JSON con todas las métricas
    """
    return jsonify(metricas)

@app.route('/api/datos', methods=['GET'])
def obtener_datos():
    """
    API endpoint para obtener los datos de entrenamiento
    Retorna: JSON con los datos utilizados en el entrenamiento
    """
    return jsonify(datos)

@app.route('/api/predicciones_rango', methods=['POST'])
def predicciones_rango():
    """
    API endpoint para obtener predicciones en un rango de valores
    Recibe: JSON con 'min' y 'max'
    Retorna: JSON con arrays de años y salarios predichos
    """
    try:
        if modelo is None:
            return jsonify({
                'error': 'El modelo no está disponible.'
            }), 500
        
        data = request.get_json()
        min_anos = float(data.get('min', 0))
        max_anos = float(data.get('max', 20))
        puntos = int(data.get('puntos', 50))
        
        # Generar rango de valores
        X_range = np.linspace(min_anos, max_anos, puntos).reshape(-1, 1)
        y_pred = modelo.predict(X_range)
        
        return jsonify({
            'anos': X_range.flatten().tolist(),
            'salarios': y_pred.tolist(),
            'exito': True
        })
    
    except Exception as e:
        return jsonify({
            'error': f'Error al generar predicciones: {str(e)}'
        }), 500

@app.route('/api/info_modelo', methods=['GET'])
def info_modelo():
    """
    API endpoint para obtener información general del modelo
    """
    if modelo is None:
        return jsonify({
            'disponible': False,
            'mensaje': 'El modelo no ha sido entrenado.'
        })
    
    return jsonify({
        'disponible': True,
        'tipo': 'Regresión Lineal Simple',
        'variable_independiente': 'Años de Experiencia',
        'variable_dependiente': 'Salario',
        'coeficiente': metricas.get('coeficiente', 0),
        'intercepto': metricas.get('intercepto', 0),
        'r2_score': metricas.get('r2_score', 0),
        'muestras_totales': metricas.get('total_muestras', 0),
        'muestras_entrenamiento': metricas.get('muestras_entrenamiento', 0),
        'muestras_prueba': metricas.get('muestras_prueba', 0)
    })

@app.route('/favicon.ico')
def favicon():
    """Manejo del favicon para evitar errores 404"""
    return '', 204

@app.errorhandler(404)
def page_not_found(e):
    """Manejo de errores 404"""
    return jsonify({
        'error': '404 - Página no encontrada',
        'mensaje': 'La ruta solicitada no existe en el servidor.'
    }), 404

@app.errorhandler(500)
def internal_error(e):
    """Manejo de errores 500"""
    return jsonify({
        'error': '500 - Error interno del servidor',
        'mensaje': 'Ocurrió un error en el servidor. Por favor intenta nuevamente.'
    }), 500

if __name__ == '__main__':
    # Verificar si el modelo existe
    if not os.path.exists(MODELO_PATH):
        print("\n" + "=" * 70)
        print(" ADVERTENCIA: El modelo no existe")
        print("=" * 70)
        print("\nPara entrenar el modelo, ejecuta:")
        print("  python train_model.py")
        print("\nLuego vuelve a ejecutar esta aplicación.")
        print("=" * 70 + "\n")
    else:
        print("\n" + "=" * 70)
        print("✓ Modelo cargado exitosamente")
        print("=" * 70)
        print(f"\nMétricas del modelo:")
        print(f"  → R² Score: {metricas.get('r2_score', 0):.4f}")
        print(f"  → RMSE: ${metricas.get('rmse', 0):,.2f}")
        print(f"  → Muestras: {metricas.get('total_muestras', 0)}")
        print("=" * 70 + "\n")
    
    # Iniciar servidor
    print(" Iniciando servidor Flask...")
    print(" Accede a la aplicación en: http://127.0.0.1:5000")
    print(" Presiona CTRL+C para detener el servidor\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
