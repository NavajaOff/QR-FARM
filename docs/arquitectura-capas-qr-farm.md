# Diagrama de Capas - QR-Farm

## Arquitectura del Sistema

Este diagrama muestra la arquitectura en capas del proyecto QR-Farm, siguiendo principios de arquitectura limpia y separación de responsabilidades.

```mermaid
flowchart TB
    subgraph Frontend["🎨 Capa de Presentación (Frontend)"]
        direction TB
        Views["Views<br/>- admin/*<br/>- user/*<br/>- public/*"]
        Components["Components<br/>- QrScanner<br/>- RegistroVacunacionBase<br/>- TenantSelector<br/>- PotreroCard/Modal"]
        Composables["Composables<br/>- useGanado<br/>- usePotreros<br/>- useReportes<br/>- useUsuarios<br/>- useTenants"]
        ServicesFrontend["Services (API Client)<br/>- api.js (Axios)<br/>- authService.js<br/>- qr.ts"]
        Router["Router<br/>- index.js<br/>- auth.js"]
        Assets["Assets<br/>- js/*<br/>- css/*<br/>- images/*"]
        SocketClient["Socket Client<br/>- socket.js"]
    end

    subgraph API["🌐 Capa de API / Rutas"]
        direction TB
        Routes["Routes (Blueprints)<br/>- animal_routes.py<br/>- potrero_routes.py<br/>- usuario_routes.py<br/>- vacunacion_routes.py<br/>- reporte_routes.py<br/>- tenant_routes.py"]
        Middleware["Middleware<br/>- token_required<br/>- tenant_required<br/>- permission_required"]
    end

    subgraph Controllers["🎮 Capa de Controladores"]
        direction TB
        AnimalCtrl["AnimalController"]
        PotreroCtrl["PotreroController"]
        UsuarioCtrl["UsuarioController"]
        VacunacionCtrl["VacunacionController"]
        ReporteCtrl["ReporteController"]
        TenantCtrl["TenantController"]
    end

    subgraph Services["⚙️ Capa de Servicios (Lógica de Negocio)"]
        direction TB
        AnimalSvc["AnimalService<br/>(GanadoService)"]
        PotreroSvc["PotreroService"]
        UsuarioSvc["UsuarioService"]
        VacunacionSvc["VacunacionService"]
        ReporteSvc["ReporteService"]
        TenantSvc["TenantService"]
        QrSvc["QrService"]
    end

    subgraph Models["📦 Capa de Modelos"]
        direction TB
        AnimalModel["Animal Model"]
        PotreroModel["Potrero Model"]
        UsuarioModel["Usuario Model"]
        VacunacionModel["Vacunacion Model"]
        TenantModel["Tenant Model"]
        HistorialModel["HistorialPotrero Model"]
    end

    subgraph Database["💾 Capa de Base de Datos"]
        direction TB
        DBConnection["Database Connection<br/>- db.py<br/>- get_connection()"]
        Migrations["Migrations<br/>- Alembic<br/>- versions/*"]
        Seeders["Seeders<br/>- CLI scripts"]
    end

    subgraph Infrastructure["🔧 Capa de Infraestructura"]
        direction TB
        AuthUtils["Auth Utils<br/>- auth.py (JWT)<br/>- permissions.py"]
        TenantUtils["Tenant Utils<br/>- tenant.py<br/>- init_super_admin.py"]
        Config["Config<br/>- config.py<br/>- .env"]
        CLI["CLI<br/>- secure_seed.py"]
    end

    subgraph WebSockets["📡 Capa de WebSockets (Real-time)"]
        direction TB
        SocketIO["SocketIO Server<br/>- emit_update()<br/>- Event handlers"]
        Events["Events<br/>- animal_created<br/>- animal_updated<br/>- potrero_created<br/>- usuario_updated"]
    end

    %% Dependencias Frontend -> API
    ServicesFrontend --> Routes
    SocketClient --> SocketIO
    Router --> ServicesFrontend
    Composables --> ServicesFrontend
    Components --> Composables
    Views --> Components
    Views --> Router
    Assets --> Views

    %% Dependencias API -> Controllers
    Routes --> Middleware
    Routes --> AnimalCtrl
    Routes --> PotreroCtrl
    Routes --> UsuarioCtrl
    Routes --> VacunacionCtrl
    Routes --> ReporteCtrl
    Routes --> TenantCtrl
    Middleware --> AuthUtils
    Middleware --> TenantUtils

    %% Dependencias Controllers -> Services
    AnimalCtrl --> AnimalSvc
    PotreroCtrl --> PotreroSvc
    UsuarioCtrl --> UsuarioSvc
    VacunacionCtrl --> VacunacionSvc
    ReporteCtrl --> ReporteSvc
    TenantCtrl --> TenantSvc
    AnimalCtrl --> QrSvc

    %% Dependencias Services -> Models
    AnimalSvc --> AnimalModel
    PotreroSvc --> PotreroModel
    UsuarioSvc --> UsuarioModel
    VacunacionSvc --> VacunacionModel
    TenantSvc --> TenantModel
    PotreroSvc --> HistorialModel

    %% Dependencias Models -> Database
    AnimalModel --> DBConnection
    PotreroModel --> DBConnection
    UsuarioModel --> DBConnection
    VacunacionModel --> DBConnection
    TenantModel --> DBConnection
    HistorialModel --> DBConnection

    %% Dependencias Database -> Infrastructure
    DBConnection --> Config
    Migrations --> DBConnection
    Seeders --> DBConnection
    Seeders --> CLI

    %% Dependencias Services -> Infrastructure
    AnimalSvc --> AuthUtils
    AnimalSvc --> TenantUtils
    PotreroSvc --> TenantUtils
    UsuarioSvc --> AuthUtils
    UsuarioSvc --> TenantUtils
    ReporteSvc --> TenantUtils

    %% Dependencias Controllers -> WebSockets
    AnimalCtrl --> SocketIO
    PotreroCtrl --> SocketIO
    UsuarioCtrl --> SocketIO
    SocketIO --> Events

    %% Estilos
    classDef frontend fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef api fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef controllers fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef services fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef models fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef database fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    classDef infrastructure fill:#e0f2f1,stroke:#004d40,stroke-width:2px
    classDef websockets fill:#f1f8e9,stroke:#33691e,stroke-width:2px

    class Views,Components,Composables,ServicesFrontend,Router,Assets,SocketClient frontend
    class Routes,Middleware api
    class AnimalCtrl,PotreroCtrl,UsuarioCtrl,VacunacionCtrl,ReporteCtrl,TenantCtrl controllers
    class AnimalSvc,PotreroSvc,UsuarioSvc,VacunacionSvc,ReporteSvc,TenantSvc,QrSvc services
    class AnimalModel,PotreroModel,UsuarioModel,VacunacionModel,TenantModel,HistorialModel models
    class DBConnection,Migrations,Seeders database
    class AuthUtils,TenantUtils,Config,CLI infrastructure
    class SocketIO,Events websockets
```

## Descripción de Capas

### 🎨 Capa de Presentación (Frontend)
- **Views**: Componentes de página principales (admin, user, public)
- **Components**: Componentes reutilizables de Vue
- **Composables**: Lógica reactiva reutilizable (Vue 3 Composition API)
- **Services**: Cliente HTTP (Axios) y servicios de autenticación
- **Router**: Enrutamiento y navegación
- **Assets**: Recursos estáticos (JS, CSS, imágenes)
- **Socket Client**: Cliente WebSocket para actualizaciones en tiempo real

### 🌐 Capa de API / Rutas
- **Routes**: Blueprints de Flask que definen los endpoints REST
- **Middleware**: Decoradores de autenticación y autorización (`token_required`, `tenant_required`, `permission_required`)

### 🎮 Capa de Controladores
- **Controllers**: Orquestan las peticiones HTTP, validan entrada y formatean respuestas
- Cada controlador maneja un recurso específico (Animal, Potrero, Usuario, etc.)

### ⚙️ Capa de Servicios (Lógica de Negocio)
- **Services**: Contienen la lógica de negocio y reglas del dominio
- **QrService**: Generación y procesamiento de códigos QR
- Los servicios son independientes de la capa de presentación y base de datos

### 📦 Capa de Modelos
- **Models**: Representan las entidades del dominio
- Contienen la estructura de datos y métodos de transformación
- Son agnósticos de la base de datos

### 💾 Capa de Base de Datos
- **DB Connection**: Gestión de conexiones MySQL
- **Migrations**: Scripts de Alembic para versionado del esquema
- **Seeders**: Scripts para poblar datos iniciales

### 🔧 Capa de Infraestructura
- **Auth Utils**: JWT, validación de tokens, permisos
- **Tenant Utils**: Multi-tenancy, gestión de tenants
- **Config**: Configuración de la aplicación
- **CLI**: Comandos de línea para administración

### 📡 Capa de WebSockets (Real-time)
- **SocketIO Server**: Servidor WebSocket para actualizaciones en tiempo real
- **Events**: Eventos emitidos cuando hay cambios (creación, actualización, eliminación)

## Principios de Arquitectura

1. **Separación de Responsabilidades**: Cada capa tiene una responsabilidad única
2. **Dependencias Unidireccionales**: Las capas superiores dependen de las inferiores, nunca al revés
3. **Independencia de Framework**: Los servicios y modelos son independientes de Flask/Vue
4. **Testabilidad**: Cada capa puede ser testeada de forma independiente
5. **Escalabilidad**: Fácil agregar nuevas funcionalidades sin afectar otras capas

## Flujo de Datos

1. **Frontend** → Usuario interactúa con la interfaz
2. **API/Routes** → Recibe la petición HTTP y aplica middleware
3. **Controllers** → Valida y orquesta la petición
4. **Services** → Ejecuta la lógica de negocio
5. **Models** → Representa los datos del dominio
6. **Database** → Persiste o recupera datos
7. **WebSockets** → Emite actualizaciones en tiempo real a los clientes conectados

