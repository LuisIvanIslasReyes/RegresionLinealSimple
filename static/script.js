/**
 * Script JavaScript para la aplicación de Regresión Lineal Simple
 * Maneja la interactividad, predicciones y gráficas
 */

// ============================================
// VARIABLES GLOBALES
// ============================================

let chartInstance = null;
const API_BASE_URL = window.location.origin;

// ============================================
// INICIALIZACIÓN
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('Aplicación de Regresión Lineal Simple iniciada');
    
    initializeForm();
    initializeChart();
    syncInputs();
});

// ============================================
// FORMULARIO DE PREDICCIÓN
// ============================================

function initializeForm() {
    const form = document.getElementById('predictForm');
    const yearsInput = document.getElementById('yearsInput');
    const yearsSlider = document.getElementById('yearsSlider');
    
    if (!form) return;
    
    // Sincronizar input y slider
    yearsInput.addEventListener('input', function() {
        yearsSlider.value = this.value;
    });
    
    yearsSlider.addEventListener('input', function() {
        yearsInput.value = this.value;
    });
    
    // Manejar envío del formulario
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        realizarPrediccion();
    });
    
    // Realizar predicción inicial
    if (!yearsInput.disabled) {
        realizarPrediccion();
    }
}

function syncInputs() {
    const yearsInput = document.getElementById('yearsInput');
    const yearsSlider = document.getElementById('yearsSlider');
    
    if (yearsInput && yearsSlider) {
        yearsInput.value = yearsSlider.value;
    }
}

// ============================================
// PREDICCIÓN
// ============================================

async function realizarPrediccion() {
    const yearsInput = document.getElementById('yearsInput');
    const resultDiv = document.getElementById('predictionResult');
    const errorDiv = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    
    const anosExperiencia = parseFloat(yearsInput.value);
    
    // Validación básica
    if (isNaN(anosExperiencia) || anosExperiencia < 0) {
        mostrarError('Por favor ingresa un valor válido (mayor o igual a 0)');
        return;
    }
    
    // Ocultar mensajes previos
    if (errorDiv) errorDiv.style.display = 'none';
    if (resultDiv) resultDiv.style.display = 'none';
    
    try {
        // Realizar petición al API
        const response = await fetch(`${API_BASE_URL}/api/predecir`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                anos_experiencia: anosExperiencia
            })
        });
        
        const data = await response.json();
        
        if (data.exito) {
            mostrarResultado(data);
        } else {
            mostrarError(data.error || 'Error al realizar la predicción');
        }
        
    } catch (error) {
        console.error('Error:', error);
        mostrarError('Error de conexión. Por favor intenta nuevamente.');
    }
}

function mostrarResultado(data) {
    const resultDiv = document.getElementById('predictionResult');
    const resultYears = document.getElementById('resultYears');
    const resultSalary = document.getElementById('resultSalary');
    
    if (!resultDiv) return;
    
    // Actualizar valores
    resultYears.textContent = `${data.anos_experiencia} años`;
    resultSalary.textContent = data.salario_formateado;
    
    // Mostrar resultado con animación
    resultDiv.style.display = 'block';
    resultDiv.classList.add('pulse');
    
    setTimeout(() => {
        resultDiv.classList.remove('pulse');
    }, 1000);
    
    // Actualizar gráfica si existe
    if (chartInstance) {
        actualizarPuntoPrediccion(data.anos_experiencia, data.salario_predicho);
    }
}

function mostrarError(mensaje) {
    const errorDiv = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    const resultDiv = document.getElementById('predictionResult');
    
    if (!errorDiv) return;
    
    errorText.textContent = mensaje;
    errorDiv.style.display = 'flex';
    
    if (resultDiv) {
        resultDiv.style.display = 'none';
    }
    
    // Ocultar error después de 5 segundos
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

// ============================================
// GRÁFICA INTERACTIVA
// ============================================

async function initializeChart() {
    const canvas = document.getElementById('interactiveChart');
    if (!canvas) return;
    
    try {
        // Obtener datos del modelo
        const [datosResponse, metricasResponse] = await Promise.all([
            fetch(`${API_BASE_URL}/api/datos`),
            fetch(`${API_BASE_URL}/api/metricas`)
        ]);
        
        const datos = await datosResponse.json();
        const metricas = await metricasResponse.json();
        
        // Preparar datos para la gráfica
        const datosEntrenamiento = datos.X_train.map((x, i) => ({
            x: x,
            y: datos.y_train[i]
        }));
        
        const datosPrueba = datos.X_test.map((x, i) => ({
            x: x,
            y: datos.y_test[i]
        }));
        
        // Generar línea de regresión
        const xMin = Math.min(...datos.X_all);
        const xMax = Math.max(...datos.X_all);
        const lineaRegresion = [];
        
        for (let x = xMin; x <= xMax; x += 0.5) {
            const y = metricas.intercepto + (metricas.coeficiente * x);
            lineaRegresion.push({ x: x, y: y });
        }
        
        // Crear gráfica
        const ctx = canvas.getContext('2d');
        chartInstance = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [
                    {
                        label: 'Datos de Entrenamiento',
                        data: datosEntrenamiento,
                        backgroundColor: 'rgba(91, 124, 153, 0.6)',
                        borderColor: 'rgba(44, 62, 80, 0.8)',
                        borderWidth: 2,
                        pointRadius: 6,
                        pointHoverRadius: 8,
                    },
                    {
                        label: 'Datos de Prueba',
                        data: datosPrueba,
                        backgroundColor: 'rgba(127, 163, 201, 0.6)',
                        borderColor: 'rgba(52, 73, 94, 0.8)',
                        borderWidth: 2,
                        pointRadius: 6,
                        pointHoverRadius: 8,
                    },
                    {
                        label: 'Línea de Regresión',
                        data: lineaRegresion,
                        type: 'line',
                        borderColor: 'rgba(231, 76, 60, 0.8)',
                        borderWidth: 3,
                        fill: false,
                        pointRadius: 0,
                        pointHoverRadius: 0,
                        tension: 0
                    },
                    {
                        label: 'Predicción Actual',
                        data: [],
                        backgroundColor: 'rgba(39, 174, 96, 1)',
                        borderColor: 'rgba(39, 174, 96, 1)',
                        borderWidth: 3,
                        pointRadius: 10,
                        pointHoverRadius: 12,
                        pointStyle: 'star',
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            font: {
                                size: 12,
                                family: 'Inter, sans-serif'
                            },
                            padding: 15,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(44, 62, 80, 0.9)',
                        titleFont: {
                            size: 14,
                            family: 'Inter, sans-serif'
                        },
                        bodyFont: {
                            size: 13,
                            family: 'Inter, sans-serif'
                        },
                        padding: 12,
                        cornerRadius: 8,
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                label += `(${context.parsed.x.toFixed(1)} años, $${context.parsed.y.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",")})`;
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'linear',
                        position: 'bottom',
                        title: {
                            display: true,
                            text: 'Años de Experiencia',
                            font: {
                                size: 14,
                                weight: 'bold',
                                family: 'Inter, sans-serif'
                            },
                            color: '#2C3E50'
                        },
                        grid: {
                            color: 'rgba(91, 124, 153, 0.1)',
                            lineWidth: 1
                        },
                        ticks: {
                            font: {
                                size: 12,
                                family: 'Inter, sans-serif'
                            },
                            color: '#5A6C7D'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Salario ($)',
                            font: {
                                size: 14,
                                weight: 'bold',
                                family: 'Inter, sans-serif'
                            },
                            color: '#2C3E50'
                        },
                        grid: {
                            color: 'rgba(91, 124, 153, 0.1)',
                            lineWidth: 1
                        },
                        ticks: {
                            font: {
                                size: 12,
                                family: 'Inter, sans-serif'
                            },
                            color: '#5A6C7D',
                            callback: function(value) {
                                return '$' + value.toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
                            }
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    intersect: false
                }
            }
        });
        
        console.log('✅ Gráfica interactiva creada exitosamente');
        
    } catch (error) {
        console.error('Error al crear la gráfica:', error);
    }
}

function actualizarPuntoPrediccion(x, y) {
    if (!chartInstance) return;
    
    // Actualizar dataset de predicción actual
    chartInstance.data.datasets[3].data = [{ x: x, y: y }];
    chartInstance.update('none'); // Actualizar sin animación
}

// ============================================
// UTILIDADES
// ============================================

function formatearMoneda(valor) {
    return new Intl.NumberFormat('es-MX', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(valor);
}

function formatearNumero(valor, decimales = 2) {
    return valor.toFixed(decimales).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// ============================================
// MANEJO DE ERRORES GLOBAL
// ============================================

window.addEventListener('error', function(e) {
    console.error('Error global:', e.error);
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('Promesa rechazada:', e.reason);
});

console.log('✅ Script JavaScript cargado exitosamente');
