# Tarea: Pruebas de Rendimiento con JMeter sobre la API REST de Consulta y Pago de Deudas
*(10 puntos sobre total de nota del curso)*

## Objetivo

Evaluar el rendimiento de la API REST que gestiona la consulta y el pago de deudas entre un Banco y una Telco, utilizando Apache JMeter para simular:

- Operaciones de consulta (lectura)
- Operaciones de pago (escritura)
- Impacto del parámetro `--limit-concurrency` de Uvicorn

## Instrucciones

### A. Configuración de entorno

Tener en ejecución:

- La API del Banco y la de la Telco (en puertos distintos)
- Ambas APIs deben ejecutarse con Uvicorn
- Instalar Apache JMeter

### B. Diseño del Plan de Pruebas en JMeter (5 puntos)

#### 1. Crea un plan de prueba con dos Thread Groups (2 puntos):

- **Grupo 1 - Lectura:** Prueba el endpoint `consultar_deuda(ci)` con 50, 100 y 200 usuarios simultáneos.
- **Grupo 2 - Escritura:** Prueba el endpoint `pagar_deuda(...)` con 10, 30 y 50 usuarios, usando datos variados. *(Simular pagos de 1 gs para evitar la cancelación rápida de la factura.)*

#### 2. Configura (2 puntos):

- HTTP Request Sampler para cada endpoint.
- Listeners como Summary Report, Aggregate Report.

#### 3. Incluye casos válidos e inválidos (1 punto):

- Para evaluar también el manejo de errores (respuestas 400, 404, 422, etc.).

### C. Pruebas con --limit-concurrency en Uvicorn (5 puntos)

1. Leer sobre el parámetro `--limit-concurrency` del servidor uvicorn utilizado.
2. Ejecuta el servidor de la API del Banco con 2 distintas configuraciones de concurrencia:

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, backlog=1000, limit_concurrency=20)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, backlog=1000, limit_concurrency=50)
```

Por cada configuración, repite ejecuta las pruebas de JMeter  

Analiza el impacto:

¿Cómo afecta el valor de limit-concurrency en la latencia, throughput y porcentaje de errores? Enviar un cuadro comparativo de resultados usando limit_concurrency 20 y 50 (captura pantalla del resultado jmeter) (3 puntos)

¿Cuál parece ser un valor óptimo para el contexto de esta API? (2 puntos)

Entrega

Sube un archivo .zip que incluya:

El plan de prueba .jmx.

Código de API e instrucciones para ejecutarlo (puede ser URL a repositorio gitlab)

Capturas de pantalla con los resultados para cada configuracion de --limit-concurrency