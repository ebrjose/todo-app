# Todo App

Lista de tareas con recordatorios por email.

- **Backend:** Django 5.2 + Django REST Framework (auth por token), Postgres 16
- **Recordatorios:** Celery + Redis. `beat` revisa cada minuto las tareas con `remind_at` vencido y `worker` envía el email una sola vez.
- **Frontend:** React + Vite, servido por nginx, que además hace de proxy de `/api`, `/admin` y `/static` hacia Django.
- **Email en desarrollo:** Mailpit (SMTP falso con interfaz web).

## Estructura

```
backend/    Django (config/, accounts/, todos/), Dockerfile
frontend/   React + Vite, nginx.conf, Dockerfile
docker-compose.yml
```

## Levantar

```bash
docker compose up -d --build
```

| URL | Qué es |
|---|---|
| http://localhost:6780 | App |
| http://localhost:6780/admin/ | Admin de Django |
| http://localhost:6725 | Mailpit (emails enviados) |

Los puertos están ligados a `127.0.0.1`. Las migraciones corren solas al arrancar el servicio `backend`.

Crear un superusuario para el admin:

```bash
docker compose exec backend python manage.py createsuperuser
```

## Tests

```bash
docker compose run --rm -e DJANGO_MIGRATE=0 backend python manage.py test
```

## Desarrollo del frontend con hot reload

Con el stack levantado:

```bash
cd frontend
npm install
npm run dev   # http://localhost:6773, /api va al stack en :6780
```

## Configuración

Todas las variables tienen un valor por defecto para desarrollo en `docker-compose.yml`. Para cambiarlas, copia `.env.example` a `.env`. Ahí también está el ejemplo para usar un SMTP real en lugar de Mailpit.

## API

| Método | Ruta | |
|---|---|---|
| POST | `/api/auth/register/` | `{username, email, password}` → `{token, user}` |
| POST | `/api/auth/login/` | `{username, password}` → `{token, user}` |
| POST | `/api/auth/logout/` | invalida el token |
| GET | `/api/auth/me/` | usuario actual |
| GET/POST | `/api/tasks/` | listar / crear |
| GET/PATCH/DELETE | `/api/tasks/{id}/` | ver / editar / borrar |
| GET | `/api/health/` | healthcheck (sin auth) |

Las rutas protegidas usan el header `Authorization: Token <token>`. Si cambias `remind_at` de una tarea, el recordatorio se vuelve a enviar.
