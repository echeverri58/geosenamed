# Datos Sensibles Georreferenciados · SENA

Aplicación web de una sola página (sin frameworks ni instalación) que georreferencia los
registros de la **Ficha del Ciudadano** sobre un mapa de Colombia, con mapa de calor,
indicadores, filtros y análisis por comuna y barrio de Medellín.

**Creado por el instructor John Alexander Echeverry Ocampo · SENA**

---

## Cómo usarla

1. Abre **`index.html`** con doble clic (Chrome, Edge o Firefox).
2. Escribe la **clave de acceso: `kpo2026`** (se puede cambiar en `index.html`,
   variable `CLAVE_ACCESO`).
3. La aplicación ya trae los **666 registros cargados y georreferenciados**: no hay que
   subir nada.
4. Botones útiles:
   - **Centrar en Medellín** (chincheta en el mapa): comunas, barrios y detalle por dirección.
   - **Marcadores / Mapa de calor / Comunas de Medellín**: capas del mapa.
   - **Exportar CSV** y **Plantilla**: descargas de los datos filtrados o de un formato de ejemplo.
   - **Cargar / Carpeta**: solo si quieres reemplazar los datos por una ficha nueva.

> La clave es un control de acceso básico del lado del navegador: evita miradas casuales,
> pero no cifra la información. Los datos viajan dentro del archivo HTML.
> Los mosaicos del mapa y las librerías (Leaflet, Chart.js, SheetJS) se cargan desde CDN,
> así que la primera vez necesita conexión a internet.

## Qué incluye

| Sección | Contenido |
|---|---|
| Mapa | OpenStreetMap, marcadores agrupados, mapa de calor ponderado, 16 comunas de Medellín con coropleta |
| Ficha | Datos completos de cada persona, teléfonos y correo clicables |
| KPIs | Total, edad promedio, % mujeres/hombres, ciudad y EPS con más registros |
| Análisis | 9 gráficas + bloque específico de Medellín (top 12 barrios y distribución por comuna) |
| Filtros | Ciudad, sexo, rango de edad, EPS, grado de educación y búsqueda libre |
| Datos | Tabla paginada de los registros filtrados |

## Fuentes de datos

- **`FichaCiudadano.xls`** (+ carpeta `FichaCiudadano_archivos`): exportación «página web de
  Excel» de la ficha. La app lee la hoja con los 666 registros.
- **`medellin.xlsx`**: geocodificación catastral por dirección (283 filas con latitud,
  longitud, barrio y comuna). Se usa para ubicar los 287 registros de Medellín.
- **`Comunas_Medellin.geojson`**: límites de las 16 comunas (geometría simplificada ~11 m).
- Diccionario interno de los 46 municipios del país para el resto de registros.

Detalle de Medellín: 236 registros por dirección catastral, 45 dentro de su comuna y 6 a
nivel municipal (direcciones que no se pudieron geocodificar).

## Publicar o actualizar en GitHub

**Opción fácil (Windows):** doble clic en **`PUBLICAR EN GITHUB.bat`** y elige en el menú:

1. Subir todo a GitHub — usa la **sesión de GitHub guardada** en el equipo (no pide token)
2. Subir con un token — si no hay sesión guardada
3. Subir y vigilar cambios — resube solo al detectar cambios
4. Solo preparar el repositorio local

**Opción consola:**

```bash
# Sube todo usando las credenciales guardadas en Windows (sin token)
python publicar_github.py --sin-token

# Con token (lo pide de forma oculta)
python publicar_github.py --repo geosenamed

# Vigilar cambios y resubir
python publicar_github.py --repo geosenamed --watch

# Otras opciones
python publicar_github.py --repo mi-repositorio --private --pages
python publicar_github.py --diagnostico --repo geosenamed   # revisa permisos sin subir
python publicar_github.py --local      # solo repositorio local y commit
python publicar_github.py --dry-run    # muestra qué subiría, sin cambios
```

La primera vez que subas desde un equipo, Git te pedirá iniciar sesión en GitHub y
guardará la credencial; después `--sin-token` funciona solo. Si prefieres token, créalo en
https://github.com/settings/tokens con el permiso **`repo`** (clásico) o con
**Contents: Read and write** (fine-grained, incluyendo el repositorio).

Archivos que **no** se suben: los mayores de 50 MB (por ejemplo `colombia-261118.osm.pbf`),
`*.zip`, `*.crdownload` y carpetas ocultas de caché.

Si activas `--pages`, el sitio queda en
`https://<usuario>.github.io/<repositorio>/`.

## Tecnologías

HTML/CSS/JS sin frameworks · Leaflet 1.9.4 · Leaflet.markercluster 1.5.3 · leaflet.heat 0.2.0 ·
Chart.js 4.4.3 · SheetJS · Nominatim (solo al geocodificar datos nuevos) ·
OpenStreetMap (mosaicos OSM France / Esri) · CARTO no se usa (exige clave).

## Estructura

```
index.html                  ← la aplicación completa con los datos incrustados
PUBLICAR EN GITHUB.bat      ← doble clic para publicar (menú)
publicar_github.py          ← script para publicar/actualizar en GitHub
FichaCiudadano.xls          ← fuente original de la ficha
FichaCiudadano_archivos/    ← hojas de la exportación web de Excel
medellin.xlsx               ← geocodificación catastral de Medellín
Comunas_Medellin.geojson    ← límites de las comunas de Medellín
logo.png                    ← logo SENA (también incrustado en el HTML)
```
