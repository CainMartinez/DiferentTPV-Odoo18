# Diferent TPV - Sistema de Hostelería para Odoo 18

Este proyecto es una implementación completa de un **sistema TPV para hostelería** construido sobre Odoo 18. Incluye gestión de salas, mesas, pedidos y control de inventario en tiempo real, diseñado específicamente para restaurantes y bares.

## 🏪 Características Principales

- **Gestión de Salas**: Organiza tu local en diferentes áreas (comedor, terraza, bar, etc.)
- **Control de Mesas**: Sistema visual de mesas con estados en tiempo real
- **Pedidos por Mesa**: Gestión completa del flujo de pedidos desde mesa hasta cocina
- **Control de Stock**: Verificación automática de disponibilidad de productos
- **Interface Intuitiva**: Vistas kanban para una gestión visual eficiente
- **Multi-usuario**: Soporte para múltiples camareros y roles

## 📁 Estructura del Proyecto

```
odoo18-project/
├── addons/
│   └── custom_module/                    # Módulo Diferent TPV
│       ├── __init__.py
│       ├── __manifest__.py              # Configuración del módulo
│       ├── models/                      # Modelos de datos
│       │   ├── __init__.py
│       │   ├── diferent_room.py         # Modelo de salas
│       │   ├── diferent_table.py        # Modelo de mesas
│       │   └── diferent_order.py        # Modelo de pedidos
│       ├── views/                       # Interfaces de usuario
│       │   ├── diferent_room_views.xml  # Vistas de salas
│       │   ├── diferent_table_views.xml # Vistas de mesas
│       │   ├── diferent_order_views.xml # Vistas de pedidos
│       │   └── diferent_room_menu.xml   # Menús principales
│       ├── security/                    # Permisos y seguridad
│       │   └── ir.model.access.csv
│       └── data/                        # Datos iniciales
│           └── diferent_data.xml
├── config/
│   └── odoo.conf                        # Configuración de Odoo
├── .env                                 # Variables de entorno
├── .env.example                         # Plantilla de variables
├── docker-compose.yml                   # Configuración Docker
├── Dockerfile                           # Imagen personalizada
├── requirements.txt                     # Dependencias Python
├── .gitignore                          # Archivos ignorados por Git
└── README.md
```

## 🛠️ Requisitos Previos

Asegúrate de tener instalado:

- **Docker** (versión 20.10 o superior)
- **Docker Compose** (versión 1.29 o superior)

Verifica la instalación:

```bash
docker --version
docker-compose --version
```

## ⚙️ Configuración Inicial

### 1. Configurar Variables de Entorno

Copia el archivo de ejemplo y personalízalo:

```bash
cp .env.example .env
```

Edita `.env` con tus credenciales:

```env
# Database Configuration
DB_NAME=odoo_db
DB_USER=odoo_user
DB_PASSWORD=mi_password_seguro
DB_HOST=db
DB_PORT=5432

# Odoo Configuration
HTTP_PORT=8069
ADMIN_PASSWD=admin_password_seguro

# Logging
LOG_LEVEL=info
LOG_FILE=/var/log/odoo/odoo.log

# Workers Configuration
WORKERS=2
MAX_CRON_THREADS=1

# Paths
ADDONS_PATH=/mnt/extra-addons
```

### 2. Crear Directorios Necesarios

```bash
mkdir -p addons/custom_module/{models,views,security,data}
```

## 🚀 Instalación y Ejecución

### 1. Construir e Iniciar los Contenedores

```bash
# Construir e iniciar en segundo plano
docker-compose up --build -d

# Ver logs en tiempo real
docker-compose logs -f web
```

### 2. Acceder a Odoo

Abre tu navegador y ve a: **http://localhost:8069**

### 3. Configuración Inicial de Base de Datos

En la primera ejecución:
1. **Database Name**: `odoo_db`
2. **Email**: tu email (será el admin)
3. **Password**: contraseña para el usuario admin
4. **Language**: Español
5. **Country**: España
6. **Demo Data**: ✅ (recomendado para pruebas)

### 4. Instalar el Módulo Diferent TPV

1. Ve a **Aplicaciones** en el menú principal
2. Haz clic en **"Actualizar lista de aplicaciones"**
3. Busca **"Diferent TPV"**
4. Haz clic en **"Instalar"**

## 🏃‍♂️ Guía de Uso Rápido

### 1. Configurar tu Local

**Crear Salas:**
1. Ve a **Diferent TPV > Rooms**
2. Crea salas como "Comedor Principal", "Terraza", "Zona Bar"
3. Asigna colores para identificación visual

**Configurar Mesas:**
1. Ve a **Diferent TPV > Tables**
2. Crea mesas asignándolas a cada sala
3. Define la capacidad de cada mesa

### 2. Gestionar Pedidos

**Abrir Mesa:**
1. En la vista kanban de mesas, haz clic en una mesa disponible
2. Haz clic en **"Open Table"**
3. Se creará automáticamente un nuevo pedido

**Añadir Productos:**
1. En el formulario del pedido, añade líneas de productos
2. El sistema verificará automáticamente el stock disponible
3. Añade notas especiales si es necesario

**Flujo de Estados:**
- **Draft** → **Confirmed** → **Kitchen** → **Ready** → **Served** → **Paid**

### 3. Control de Cocina

**Gestionar Preparación:**
1. Ve a **Diferent TPV > Orders**
2. Filtra por estado "In Kitchen"
3. Marca líneas individuales como "Preparing" → "Ready"

## 🔧 Comandos Útiles

### Docker

```bash
# Reiniciar solo Odoo (mantiene la DB)
docker-compose restart web

# Ver logs
docker-compose logs -f web

# Parar todo
docker-compose down

# Limpiar base de datos (¡cuidado!)
docker-compose down && docker volume rm odoo18-project_db_data

# Actualizar módulo
docker-compose exec web odoo -c /etc/odoo/odoo.conf -u custom_module -d odoo_db --stop-after-init
```

### Desarrollo

```bash
# Entrar al contenedor de Odoo
docker-compose exec web bash

# Ver logs específicos
docker-compose logs web | grep ERROR

# Backup de base de datos
docker-compose exec db pg_dump -U odoo_user odoo_db > backup.sql
```

## 📊 Módulos Base Incluidos

El proyecto incluye estos módulos esenciales de Odoo:

- **Sales Management** - Gestión de ventas
- **Purchase Management** - Gestión de compras
- **Inventory Management** - Control de stock
- **Accounting** - Contabilidad
- **Employees** - Gestión de empleados
- **Point of Sale** - TPV base de Odoo

## 🏗️ Arquitectura del Módulo

### Modelos Principales

- **`diferent.room`**: Gestión de salas del local
- **`diferent.table`**: Control de mesas y su estado
- **`diferent.order`**: Pedidos por mesa
- **`diferent.order.line`**: Líneas de productos en pedidos

### Flujo de Datos

```
Sala → Mesas → Pedido Activo → Líneas de Productos
  ↓        ↓         ↓              ↓
Color   Estado   Camarero    Stock Check
```

## 🔒 Seguridad

- Las credenciales están en variables de entorno
- El archivo `.env` está excluido del control de versiones
- Permisos granulares por modelo
- Contraseña maestra para administración de BD

## 🚀 Siguientes Pasos de Desarrollo

### Funcionalidades Planificadas

- [ ] **Vista de plano visual**: Arrastrar y soltar mesas
- [ ] **Sistema de reservas**: Gestión de reservas futuras
- [ ] **Integración con cocina**: Dashboard en tiempo real
- [ ] **Análisis de ventas**: Reportes de rendimiento
- [ ] **App móvil**: Cliente para camareros
- [ ] **Integración de pagos**: TPV físico

### Extensiones Sugeridas

- **Gestión de turnos**: Control de horarios de empleados
- **Programa de fidelización**: Puntos para clientes
- **Delivery integration**: Pedidos a domicilio
- **Inventory alerts**: Alertas de stock bajo

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## 📞 Soporte

- **Documentación**: [Odoo 18 Documentation](https://www.odoo.com/documentation/18.0/)
- **Issues**: Usa el sistema de issues de GitHub
- **Discusiones**: GitHub Discussions para preguntas generales

## 📄 Licencia

Este proyecto está bajo la **Licencia AGPL-3** - ver el archivo [LICENSE](LICENSE) para detalles.

---

**Desarrollado por**: Caín Martínez  
**Website**: https://cain-dev.es  
**Versión**: 18.0.1.0.0

> 💡 **Tip**: Para un mejor rendimiento en producción, configura `workers` > 0 y usa PostgreSQL externo.