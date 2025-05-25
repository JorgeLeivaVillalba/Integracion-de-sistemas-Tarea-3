import sqlite3
import datetime

# Crear o conectar a la base de datos
conn = sqlite3.connect('banco_telco.db')
cursor = conn.cursor()

# Tabla Clientes
cursor.execute('''
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    ci TEXT UNIQUE NOT NULL
)
''')

# Tabla CuentaDebito
cursor.execute('''
CREATE TABLE IF NOT EXISTS cuenta_debito (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    nro_cuenta TEXT NOT NULL,
    saldo REAL NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
)
''')

# Tabla FacturaPendientes
cursor.execute('''
CREATE TABLE IF NOT EXISTS factura_pendientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    nrofactura TEXT NOT NULL,
    saldoPendiente REAL NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
)
''')

# Tabla PagosServicios
cursor.execute('''
CREATE TABLE IF NOT EXISTS pagos_servicios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT NOT NULL,
    id_cuenta_debito INTEGER NOT NULL,
    monto REAL NOT NULL,
    nro_factura TEXT NOT NULL,
    FOREIGN KEY (id_cuenta_debito) REFERENCES cuenta_debito(id)
)
''')

# Datos de prueba

clientes = [
    ("Jorge", "Leiva", "1234567"),
    ("Esteban", "Quito", "2345678"),
    ("Juan", "Perez", "3456789")
]
cursor.executemany("INSERT INTO clientes (nombre, apellido, ci) VALUES (?, ?, ?)", clientes)

cuentas = [
    (1, "100-1", 500000.0),  
    (2, "100-2", 300000.0),  
    (3, "100-3", 200000.0)   
]
cursor.executemany("INSERT INTO cuenta_debito (cliente_id, nro_cuenta, saldo) VALUES (?, ?, ?)", cuentas)

facturas = [
    (1, "F-001", 500000.0),  
    (1, "F-002", 800.0),   
    (2, "F-003", 1200.0),  
    (3, "F-004", 500.0)    
]
cursor.executemany("INSERT INTO factura_pendientes (cliente_id, nrofactura, saldoPendiente) VALUES (?, ?, ?)", facturas)

# pago de ejemplo
fecha_actual = datetime.datetime.now().isoformat()
pagos = [
    (fecha_actual, 1, 500.0, "F-001")  # Pago de la factura F-001 
]

cursor.executemany("INSERT INTO pagos_servicios (fecha, id_cuenta_debito, monto, nro_factura) VALUES (?, ?, ?, ?)", pagos)

# Guardar cambios y cerrar conexión
conn.commit()
print("Base de datos creada")

# Verificar datos insertados
print("\nClientes:")
cursor.execute("SELECT * FROM clientes")
for row in cursor.fetchall():
    print(row)

print("\nCuentas de Débito:")
cursor.execute("SELECT * FROM cuenta_debito")
for row in cursor.fetchall():
    print(row)

print("\nFacturas Pendientes:")
cursor.execute("SELECT * FROM factura_pendientes")
for row in cursor.fetchall():
    print(row)

print("\nPagos de Servicios:")
cursor.execute("SELECT * FROM pagos_servicios")
for row in cursor.fetchall():
    print(row)

conn.close()