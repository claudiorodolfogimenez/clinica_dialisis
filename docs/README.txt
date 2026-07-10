# 🏥 Sistema Salud Renal

Sistema integral para la gestión de clínicas de hemodiálisis desarrollado por **Máximo Meridio** utilizando Django.

Actualmente se encuentra en producción y permite administrar pacientes, sesiones de diálisis, controles clínicos, stock e información médica desde una interfaz web.

---

# Estado del proyecto

🟢 En producción

Versión actual: **1.3**

Desarrollo activo.

---

# Objetivos

El sistema fue diseñado para digitalizar completamente la operatoria diaria de una clínica de hemodiálisis.

Entre sus objetivos se encuentran:

- Reducir el uso de planillas en papel.
- Centralizar la información clínica.
- Facilitar el trabajo de enfermería.
- Mejorar el seguimiento médico.
- Obtener reportes mensuales.
- Escalar a múltiples clínicas.

---

# Tecnologías

- Python
- Django 6
- SQLite
- Bootstrap 5
- HTML5
- CSS
- JavaScript
- Waitress
- Git
- GitHub

---

# Módulos implementados

## Pacientes

- Alta
- Baja
- Modificación
- Historia clínica
- Obra social
- Datos personales

---

## Sesiones de diálisis

- Inicio de sesión
- Finalización
- Peso inicial
- Peso final
- Tensión arterial
- Frecuencia cardíaca
- Controles horarios
- Observaciones

---

## Dashboard

- Pacientes por turno
- Estado de sesiones
- Visualización rápida

---

## Stock

- Insumos
- Control de materiales
- Administración

---

## Administración

- Usuarios
- Permisos
- Médicos
- Enfermería
- Administración

---

# Próximos módulos

- Evolución Nutricional
- Evolución Psicológica
- Monitor de Sala
- Dashboard estadístico
- Indicadores Kt/V
- Firma Digital
- Reportes avanzados
- Historia clínica ampliada

---

# Arquitectura

```
Django

├── dashboard
├── pacientes
├── sesiones
├── stock
├── nutricion
├── config
└── docs
```

---

# Documentación

Toda la documentación técnica se encuentra en la carpeta:

```
docs/
```

Incluye:

- Instalación
- Servidor
- Base de datos
- Roadmap
- Historial de cambios
- Manual de usuario

---

# Flujo de desarrollo

Producción:

```
main
```

Desarrollo:

```
desarrollo
```

Todos los cambios se realizan mediante Issues y luego se integran a producción.

---

# Roadmap

Versión 1.4

- Evolución Nutricional
- Evolución Psicológica
- Mejoras impresión mensual
- Login médicos mediante DNI

Versión 1.5

- Dashboard estadístico
- Indicadores Kt/V
- Monitor de Sala

Versión 2.0

- Multi clínica
- API REST
- Aplicación móvil

---

# Desarrollado por

**Máximo Meridio**

San Luis - Argentina

Desarrollado por Claudio Giménez.

---