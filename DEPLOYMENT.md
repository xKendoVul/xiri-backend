# Despliegue manual en Render y Supabase

El backend sigue usando Django REST Framework y JWT. Expo consume Django; Supabase aloja PostgreSQL y los archivos. No hay que sustituir el login por Supabase Auth.

## 1. Revisar y subir los cambios a GitHub

Desde la carpeta del proyecto y con el entorno virtual activado:

```bash
python manage.py test --settings=xiri_backend.test_settings
python manage.py makemigrations --check --dry-run --settings=xiri_backend.test_settings
git status
```

Incluye las carpetas de migraciones, los archivos `__init__.py`, `build.sh`, `start.sh` y `.python-version` en tu commit. Revisa los cambios y súbelos a la rama que conectarás a Render. `.env`, `env/`, `media/` y `staticfiles/` están excluidos. No agregues credenciales ni copias de datos al repositorio.

Las migraciones originales se han conservado. `price` ya existía en ellas; se restauró en el modelo y se agregó una migración que valida precios no negativos. No se han ejecutado migraciones sobre tu PostgreSQL actual.

## 2. Crear PostgreSQL en Supabase

1. Crea un proyecto en https://supabase.com/dashboard y elige una región cercana a la que usarás en Render.
2. Guarda la contraseña de la base de datos.
3. Abre **Connect** y selecciona **Session pooler**, puerto **5432**. Copia su URI de PostgreSQL, incluyendo el usuario `postgres.PROJECT_REF` y el host que muestra el panel. No uses el Transaction pooler de puerto 6543 para esta configuración.
4. Sustituye la contraseña en la URI. Si tiene caracteres especiales, codifícala como componente de URL (por ejemplo `@` → `%40`).
5. En **Integrations → Data API** (o Settings → Data API, según el panel), desactiva **Enable Data API**. Esta app accede a las tablas mediante Django y no necesita la API REST/GraphQL de Supabase. Así evitas accesos que salten los permisos de Django. Esto no sustituye ni desactiva Supabase Storage.
6. No crees las tablas a mano ni ejecutes un `schema.sql`: Django las crea con `migrate`.

Ejemplo de conexión, solo con placeholders:

```text
postgresql://postgres.PROJECT_REF:ENCODED_PASSWORD@POOLER_HOST:5432/postgres?sslmode=require
```

Documentación: https://supabase.com/docs/guides/database/connecting-to-postgres y https://supabase.com/docs/guides/api/securing-your-api.

## 3. Preparar archivos persistentes en Supabase Storage

Render Free no conserva imágenes subidas en su disco entre reinicios.

1. En **Storage**, crea un bucket llamado `media`, **privado**. Contendrá imágenes de comida y documentos de identidad; no lo hagas público.
2. Abre la configuración **S3** de Storage y genera un **Access Key ID** y un **Secret Access Key**.
3. Copia también el **endpoint S3** completo y la **región** del panel. El endpoint suele terminar en `/storage/v1/s3`; no uses solo la URL principal del proyecto.
4. Esas claves se guardan únicamente en Render. No van en Expo ni en GitHub, y no son la `anon key` o la `service_role key`.

Django ya está configurado para este bucket cuando `USE_SUPABASE_STORAGE=True`. Las imágenes siguen apareciendo en los mismos campos JSON, con URLs firmadas que duran una hora. Expo debe volver a consultar la API cuando una URL guardada haya vencido.

Documentación: https://supabase.com/docs/guides/storage/s3/authentication.

## 4. Crear el servicio en Render

En https://dashboard.render.com:

1. **New → Web Service**.
2. Conecta tu repositorio de GitHub y selecciona la rama con las correcciones.
3. Elige **Python 3** como runtime; deja Root Directory vacío si `manage.py` está en la raíz.
4. Selecciona la región y el plan **Free**.
5. Configura estos comandos:

| Campo | Valor |
|---|---|
| Build Command | `bash build.sh` |
| Start Command | `bash start.sh` |
| Health Check Path | `/health/` |

El build instala dependencias y recopila archivos estáticos. El arranque aplica migraciones y ejecuta Gunicorn. Las migraciones se ejecutan al arrancar porque el plan Free no incluye un comando pre-deploy. Si una migración falla, el servicio no arrancará; revisa sus logs. Para futuros despliegues con varias instancias, mueve las migraciones a un único paso pre-deploy.

Python está fijado a `3.14.3` en `.python-version`.

## 5. Variables de entorno en Render

Antes del primer despliegue, agrega:

| Variable | Valor |
|---|---|
| `DEBUG` | `False` |
| `SECRET_KEY` | Una clave aleatoria nueva, generada con el comando de abajo |
| `DATABASE_URL` | URI del Session pooler de Supabase |
| `ALLOWED_HOSTS` | `NOMBRE.onrender.com` (sin `https://`) |
| `CSRF_TRUSTED_ORIGINS` | `https://NOMBRE.onrender.com` |
| `CORS_ALLOW_ALL_ORIGINS` | `False` |
| `USE_SUPABASE_STORAGE` | `True` |
| `SUPABASE_STORAGE_BUCKET` | `media` |
| `SUPABASE_S3_ACCESS_KEY_ID` | Clave S3 del panel |
| `SUPABASE_S3_SECRET_ACCESS_KEY` | Secreto S3 del panel |
| `SUPABASE_S3_ENDPOINT_URL` | Endpoint S3 completo |
| `SUPABASE_S3_REGION` | Región S3 del panel |

Genera una clave localmente:

```bash
python -c 'import secrets; print(secrets.token_urlsafe(64))'
```

Render proporciona `RENDER_EXTERNAL_HOSTNAME`, que el código agrega automáticamente a `ALLOWED_HOSTS`. Cuando conozcas la URL definitiva, confirma `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS`.

En Expo nativo no necesitas un origen CORS. Si también usas Expo Web, agrega `CORS_ALLOWED_ORIGINS` con su origen exacto, por ejemplo `https://mi-app.example.com`, o `http://localhost:8081` para desarrollo web. No escribas rutas dentro del origen.

La clave secreta nueva invalida los JWT antiguos: los usuarios deben iniciar sesión de nuevo. `DB_NAME`, `DB_USER`, etc. siguen disponibles para desarrollo local, pero `DATABASE_URL` tiene prioridad.

## 6. Desplegar y crear tu administrador

1. Haz clic en **Create Web Service / Deploy**.
2. Comprueba en Logs que el build terminó, las migraciones se aplicaron y Gunicorn arrancó.
3. Visita `https://NOMBRE.onrender.com/health/`: debe responder `{"status":"ok"}`. Este endpoint no consulta la base de datos.
4. Visita `/api/gastronomy/departments/`: debe responder una lista (vacía al inicio). Esto sí comprueba acceso a PostgreSQL.
5. Para crear un administrador, usa tu terminal local: activa el entorno virtual y configura una copia local `.env` con `DATABASE_URL` apuntando a Supabase. Para mantener tu desarrollo local, respalda primero tu `.env` y restáuralo después.

```bash
python manage.py migrate
python manage.py createsuperuser
```

6. Entra en `https://NOMBRE.onrender.com/admin/` con esa cuenta. El superusuario tiene permiso de administrador en la API, aunque su campo `rol` sea `user`.
7. No ejecutes `create_test_users` en producción: crea cuentas con contraseñas conocidas.

## 7. Conservar tus datos actuales (opcional)

El despliegue crea una base nueva y vacía. No copia automáticamente los usuarios, negocios o imágenes actuales.

Antes de cambiar tu `.env`, exporta desde tu PostgreSQL local:

```bash
python manage.py dumpdata --natural-foreign --natural-primary --exclude contenttypes --exclude auth.permission --exclude sessions --exclude admin.logentry --exclude token_blacklist --output /tmp/xiri-data.json
```

Guarda esa copia de forma segura fuera del repositorio: incluye información personal y hashes de contraseñas. Luego configura `DATABASE_URL` hacia Supabase, aplica migraciones e importa:

```bash
python manage.py migrate
python manage.py loaddata /tmp/xiri-data.json
```

Haz la importación sobre una base recién creada, antes de crear nuevas cuentas o permitir registros. No uses `--fake` para ocultar errores de migración. Si importas un superusuario existente, puedes usarlo o crear otro con un username distinto.

Las imágenes se transfieren por separado. Sube el contenido de `media/` al bucket privado `media`, conservando las rutas relativas exactas. Por ejemplo, `media/platillos/vigoron.jpg` debe quedar como `platillos/vigoron.jpg` dentro del bucket. La importación de datos solo conserva los nombres de los archivos.

Restaura tu `.env` local al terminar si quieres seguir desarrollando contra PostgreSQL local.

## 8. Conectar Expo

Configura la URL base de la app según cómo esté implementado tu frontend:

```text
https://NOMBRE.onrender.com/api
```

Si tu cliente ya agrega `/api`, usa solo `https://NOMBRE.onrender.com`. Verifica que no se duplique `/api`.

Prueba registro, login, refresh, listado de negocios, subida de imágenes y visualización de las URLs devueltas. Las rutas existentes y los campos JSON se conservan; las escrituras no autorizadas se rechazan y los datos inválidos devuelven 400.

## 9. Reposo y límites gratuitos

Puedes configurar un monitor externo con GET a `/health/` cada 10 minutos para generar tráfico entrante. Eso puede evitar el reposo por inactividad, pero no garantiza disponibilidad y consume las horas gratuitas de Render. No uses `/robots.txt` como ping.

Ese ping no genera actividad de PostgreSQL y no evita una posible pausa de Supabase Free por baja actividad. Revisa las notificaciones de Supabase y reactiva el proyecto en el panel si se pausa.

## Validación realizada

- 14 pruebas de regresión con una base SQLite aislada: permisos, sincronización de precios, validaciones, correo duplicado y refresh tokens.
- Migraciones aplicadas en la base de pruebas y sin cambios de modelos pendientes.
- `collectstatic` completado con WhiteNoise.
- Comprobación de producción: quedan las recomendaciones opcionales de HSTS para subdominios y preload; no se habilitan sin conocer tu dominio.
- PostgreSQL remoto, bloqueos concurrentes y uploads reales a Supabase deberán verificarse durante tu despliegue manual. No se han creado servicios externos ni modificado tu base de datos actual.
