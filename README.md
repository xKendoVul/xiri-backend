# 🍽️ Xiri Backend

Backend API para aplicación móvil de turismo gastronómico en Nicaragua, gamificada tipo álbum de coleccionable.

![Django](https://img.shields.io/badge/Django-6.0-green)
![Python](https://img.shields.io/badge/Python-3.14-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)

---

## 📖 Descripción

**Xiri** es una aplicación que permite a los turistas descubrir y coleccionar la gastronomía Nicaragüense mediante un sistema de álbum digital. Los usuarios pueden:

- 🌎 **Explorar** platillos típicos organizados por departamento
- 📸 **Coleccionar** comidas al visitary calificar locales
- 🏆 **Completar** su álbum departamental
- 🗺️ **Seguir rutas** gastronómicas recomendadas
- 📍 **Descubrir locales** con menús y precios

### Sistema de Roles

| Rol | Descripción |
|-----|-------------|
| `user` | Explorador - Puede ver catálogo y gestionar su álbum |
| `owner` | Comerciante - Puede gestionar su(s) negocio(s) |
| `admin` | Administrador - Control total del catálogo y validaciones |

---

## 🛠️ Tecnologías

| Tecnología | Versión | Uso |
|------------|---------|-----|
| **Django** | 6.0 | Framework web |
| **Django REST Framework** | 3.17 | API REST |
| **Simple JWT** | 5.5 | Autenticación JWT |
| **PostgreSQL** | 16 | Base de datos |
| **Docker** | Latest | Contenedores |
| **Python** | 3.14 | Lenguaje |

### Librerías adicionales

- `django-cors-headers` - Manejo de CORS para Expo
- `django-environ` - Variables de entorno
- `psycopg2-binary` - Driver PostgreSQL
- `pillow` - Procesamiento de imágenes

---

## 📦 Instalación

### Requisitos Previos

- Python 3.10+
- PostgreSQL 16+ (o Docker)
- Git

### 1. Clonar el repositorio

```bash
git clone https://github.com/xKendoVul/xiri-backend.git
cd xiri-backend
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# Activar en Linux/Mac
source venv/bin/activate

# Activar en Windows
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuración

### Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# Base de datos (si usas PostgreSQL local)
DB_NAME=xiri_backend
DB_USER=postgres
DB_PASSWORD=tu_password_seguro
DB_HOST=localhost
DB_PORT=5432

# Django
DEBUG=True
SECRET_KEY=tu-clave-secreta-muy-larga-y-aleatoria
ALLOWED_HOSTS=localhost,127.0.0.1

# - CORS (para desarrollo con Expo)
CORS_ALLOWED_ORIGINS=http://localhost:8081
```

### Opción A: PostgreSQL Local

1. Instala PostgreSQL en tu sistema
2. Crea la base de datos:

```bash
createdb -U postgres xiri_backend
```

3. Configura el `.env` con tus credenciales
4. Ejecuta las migraciones (ver sección **Ejecución**)

### Opción B: Docker Compose

El proyecto incluye `compose.yaml` con PostgreSQL preconfigurado.

```bash
# Iniciar PostgreSQL con Docker
docker compose up -d postgres

# Verificar que esté corriendo
docker compose ps
```

No necesitas modificar el `.env` si usas Docker, las credenciales por defecto son:

| Variable | Valor |
|----------|-------|
| DB_NAME | xiri_backend |
| DB_USER | postgres |
| DB_PASSWORD | postgres |
| DB_HOST | localhost |
| DB_PORT | 5432 |

---

## 🚀 Ejecución

### 1. Aplicar migraciones

```bash
python manage.py migrate
```

### 2. (Opcional) Poblar datos de prueba

```bash
# Departamentos y platillos típicos de Nicaragua
python manage.py seed_data

# Usuarios de prueba
python manage.py create_test_users
```

**Usuarios de prueba creados:**

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| admin | admin123 | Admin |
| user1 | user123 | User |
| user2 | user123 | User |
| owner1 | owner123 | Owner |
| owner2 | owner123 | Owner |

### 3. Iniciar el servidor

```bash
python manage.py runserver
```

El servidor estará disponible en: **http://localhost:8000**

---

## 🔐 Endpoints Principales

### Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Registrar usuario |
| POST | `/api/auth/login/` | Login (retorna tokens) |
| POST | `/api/auth/token/refresh/` | Renovar token |

### Catálogo (Gastronomía)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/gastronomy/departments/` | Listar departamentos |
| GET | `/api/gastronomy/foods/` | Listar platillos típicos |
| GET | `/api/gastronomy/collections/` | Mi álbum |
| GET | `/api/gastronomy/routes/` | Rutas gastronómicas |

### Negocios

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET/POST | `/api/business/business/` | Mis negocios |
| GET/POST | `/api/business/menu-items/` | Platillos del menú |
| GET/POST | `/api/business/menus/` | Precios |
| PATCH | `/api/business/business/{id}/complete_profile/` | Completar datos |

### Verificación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET/POST | `/api/users/verification-requests/` | Solicitudes |
| POST | `/api/users/verification-requests/{id}/approve/` | Aprobar (admin) |
| POST | `/api/users/verification-requests/{id}/reject/` | Rechazar (admin) |

---

## 📁 Estructura del Proyecto

```
xiri-backend/
├── business/           # App de negocios y menús
│   ├── models.py      # Business, Menu, BusinessMenuItem
│   ├── views.py       # ViewSets y acciones
│   ├── serializers.py  # Serializers
│   └── admin.py       # Admin Django
│
├── gastronomy/         # App de catálogo gastronómico
│   ├── models.py      # Department, TraditionalFood, Route
│   ├── views.py       # ViewSets
│   └── admin.py       # Admin Django
│
├── users/             # App de usuarios y autenticación
│   ├── models.py      # User, VerificationRequest
│   ├── views.py       # Register, VerificationViewSet
│   └── permissions.py # Permisos personalizados
│
├── xiri_backend/      # Configuración Django
│   ├── settings.py    # Configuración principal
│   └── urls.py        # Rutas principales
│
├── media/             # Archivos subidos (imágenes)
├── schema.sql        # Script SQL del schema
├── compose.yaml      # Docker Compose
└── requirements.txt # Dependencias Python
```

---

### Admin Django

Accede a: **http://localhost:8000/admin/**

Usa las credenciales del superusuario o de `admin/admin123` si ejecutaste `create_test_users`.

---

Lo siguiente es preparar el frontend en expo, descripcion en el repo en cuestion
Frontend: https://github.com/josueespinoza2004/xiri-frontend

---

## 📝 API Documentation

La API sigue los principios REST:

- **Autenticación**: JWT Bearer Token
- **Formatos**: JSON
- **Imágenes**: Multipart form-data
- **CORS**: Habilitado para desarrollo móvil

## 👥 Equipo

Desarrollado con ❤️  para Nicaragua.
