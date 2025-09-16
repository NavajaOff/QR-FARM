# QR-FARM

Proyecto estructurado con Flask (backend) y Vue.js (frontend).

## Estructura

```
QR-FARM/
│
├── backend/                         # API Flask (MVC)
│   ├── app.py                       # Punto de entrada Flask
│   ├── config.py                    # Configuración global (BD, claves, etc.)
│   ├── requirements.txt             # Dependencias Python
│   │
│   ├── src/                         # Código fuente del backend
│   │   ├── models/                  # MODELOS (Mapeo a tablas de MySQL)
│   │   ├── controllers/             # CONTROLADORES (manejan requests)
│   │   ├── services/                # LÓGICA DE NEGOCIO
│   │   ├── routes/                  # RUTAS API REST
│   │   ├── database/                # Conexión a MySQL
│   │   └── utils/                   # Helpers / validaciones / extras
│   │
│   └── migrations/                  # Migraciones de SQLAlchemy
│
├── frontend/                        # Vue.js (Interfaz de usuario)
│   ├── package.json
│   ├── vite.config.js
│   ├── public/
│   │   └── index.html               # HTML base
│   └── src/
│       ├── main.js                  # Punto de entrada Vue
│       ├── App.vue                  # Componente raíz
│       ├── router/                  # Rutas (Vue Router)
│       ├── components/              # Componentes reutilizables
│       ├── views/                   # Vistas principales (pantallas)
│       └── assets/                  # Archivos estáticos
│           ├── css/
│           ├── images/
│           └── js/
│
└── README.md
```

## Cómo iniciar

### Backend
1. Instala dependencias:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
2. Ejecuta el servidor Flask:
   ```bash
   python app.py
   ```

### Frontend
1. Instala dependencias:
   ```bash
   cd frontend
   npm install
   ```
2. Ejecuta el servidor de desarrollo:
   ```bash
   npm run dev
   ```

---

¡Listo para desarrollar QR-FARM!