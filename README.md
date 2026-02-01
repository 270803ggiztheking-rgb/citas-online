![Sistema de Citas Online](banner.png)

# 📅 Sistema de Citas Online

Sistema completo para gestión de citas y reservaciones. **Instalable en celular como app.**

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green)
![PWA](https://img.shields.io/badge/PWA-Ready-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 📱 Instalar en Celular

1. Abre el sitio en Chrome (Android) o Safari (iOS)
2. Toca el menú de 3 puntos → **"Agregar a pantalla de inicio"**
3. ¡Listo! Tendrás la app en tu celular

## ✨ Características

- 🗓️ **Reservación online 24/7** - Clientes agendan sin llamar
- 📱 **Instalable como App** - PWA para Android e iOS
- 💬 **Chatbot integrado** - Responde preguntas automáticamente
- ⚡ **Confirmación instantánea** - Sin esperas
- 🔧 **Multi-servicio** - Define servicios con precios y duración
- 🚫 **Prevención de doble reserva** - Sistema inteligente

## 🚀 Inicio Rápido (3 pasos)

```bash
# 1. Clonar
git clone https://github.com/270803ggiztheking-rgb/citas-online.git
cd citas-online

# 2. Instalar
pip install -r requirements.txt

# 3. Ejecutar
uvicorn src.main:app --reload
```

Abre **<http://localhost:8000>** y listo.

## 🔌 Integración Simple

### Embed en tu sitio web (1 línea)

```html
<iframe src="https://tu-dominio.com/book/tu-negocio" width="100%" height="600"></iframe>
```

### Widget flotante

```html
<script src="https://tu-dominio.com/static/embed.js" data-business="tu-negocio"></script>
```

### API para tu app

```python
import requests

# Obtener horarios disponibles
response = requests.get("https://tu-dominio.com/api/businesses/1/available-times?date_str=2024-02-01&service_id=1")
horarios = response.json()["available_times"]

# Crear cita
cita = requests.post("https://tu-dominio.com/api/businesses/1/appointments", json={
    "service_id": 1,
    "client_name": "Juan",
    "client_email": "juan@email.com",
    "appointment_date": "2024-02-01",
    "appointment_time": "10:00"
})
```

## 📖 API Endpoints

| Método | Endpoint | Descripción |
| ------ | -------- | ----------- |
| POST | `/api/businesses` | Crear negocio |
| GET | `/api/businesses/{id}/services` | Listar servicios |
| GET | `/api/businesses/{id}/available-times` | Horarios disponibles |
| POST | `/api/businesses/{id}/appointments` | Crear cita |
| GET | `/api/businesses/{id}/appointments` | Listar citas |

## 💼 Casos de Uso

- Consultorios médicos y dentales
- Estéticas, spas y barberías
- Consultorías y asesorías
- Cualquier negocio con citas

## 🎨 Personalización

```css
/* Cambiar colores en static/css/styles.css */
:root {
    --primary: #6366f1;      /* Tu color principal */
    --background: #0f172a;   /* Fondo oscuro */
}
```

## 📄 Licencia

MIT License - Úsalo libremente en proyectos comerciales.

## 👤 Autor

**Gael L. Chulim G.**  
Freelance Developer & Automation Specialist  
[LinkedIn](https://www.linkedin.com/in/gael-chulim) | [GitHub](https://github.com/270803ggiztheking-rgb)

---

**¿Lo quieres para tu negocio?** Contáctame para implementación personalizada.
