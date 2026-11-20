# Convertir estos datos en un informe de Power BI

**Datos Sensibles Georreferenciados · SENA**
Creado por el instructor **John Alexander Echeverry Ocampo**

Este paquete convierte la información de la Ficha del Ciudadano (666 registros ya
georreferenciados: 287 de Medellín, 281 con comuna) en un modelo listo para Power BI:
una tabla de hechos, ocho dimensiones, las medidas DAX, un tema de colores y la guía para
armar cuatro páginas de informe.

---

## 0. Requisitos

- **Power BI Desktop** (gratis): <https://powerbi.microsoft.com/desktop/>
- Windows 10/11. No hace falta cuenta de Power BI para crear el informe; sí para publicarlo.

## 1. Qué trae la carpeta `PowerBI`

| Archivo | Para qué sirve |
|---|---|
| **`Datos_PowerBI.xlsx`** | **El archivo principal.** Modelo completo: 666 filas + 8 dimensiones, cada una como tabla de Excel. |
| `Consultas_PowerBI.m` | Código Power Query para cargar las tablas desde los CSV (ruta alternativa y refresco automático). |
| `Medidas_DAX.txt` | 30 medidas listas para copiar y pegar. |
| `Tema_SENA.json` | Tema de colores institucional (teal + verde SENA) para todo el informe. |
| `CSV/` | Los mismos datos en 9 archivos CSV (UTF-8) para la ruta Power Query o para subirlos a SharePoint/OneDrive. |
| `GUIA_POWERBI.md` | Este documento. |

## 2. Ruta recomendada: desde el Excel

1. Abre **Power BI Desktop** → **Inicio → Obtener datos → Libro de Excel**.
2. Selecciona **`Datos_PowerBI.xlsx`**.
3. En la ventana del navegador verás las tablas: marca **todas** (`HechosFicha`, `DimCiudad`,
   `DimComuna`, `DimBarrio`, `DimEPS`, `DimEducacion`, `DimSexo`, `DimInstitucion`,
   `DimCobertura`) y pulsa **Cargar**.
4. Ve a la vista **Modelo** y crea las relaciones del punto 3.
5. Crea las medidas del punto 4, aplica el tema del punto 5 y arma las páginas del punto 6.

> Si el navegador no muestra las tablas, pulsa «Transformar datos» y verifica que la hoja
> tenga la fila de encabezados en la primera fila (así está).

## 3. Relaciones del modelo

En la vista **Modelo**, arrastra el campo de la izquierda sobre el de la derecha.
Todas son **varios a uno (*:1)** y de **dirección única**:

| Tabla de hechos (`HechosFicha`) | Dimensión |
|---|---|
| `Ciudad` | `DimCiudad[Ciudad]` |
| `Comuna` | `DimComuna[Comuna]` |
| `BarrioMedellin` | `DimBarrio[Barrio]` |
| `EPS` | `DimEPS[EPS]` |
| `Educacion` | `DimEducacion[Educacion]` |
| `Sexo` | `DimSexo[Sexo]` |
| `Institucion` | `DimInstitucion[Institucion]` |
| `Cobertura` | `DimCobertura[Cobertura]` |

Consejo: oculta en `HechosFicha` las columnas que duplican la dimensión (por ejemplo
`EPS`, `Educacion`, `Sexo`) para que el panel de campos quede limpio; las relaciones siguen
funcionando.

## 4. Medidas

Abre **`Medidas_DAX.txt`**, copia cada bloque y pégalo en **Modelo → Nueva medida**.
Las principales:

| Medida | Para qué |
|---|---|
| `Total Personas` | tarjeta principal (666) |
| `Mujeres`, `Hombres`, `% Mujeres` | género |
| `Edad Promedio`, `Edad Mediana`, `Rango de Edad` | edad |
| `Ciudades`, `Comunas`, `Barrios Medellin` | cobertura |
| `Personas Medellin`, `% Medellin` | participación de Medellín (287 / 43 %) |
| `Con Direccion`, `% Georreferenciado Fino` | calidad del dato (236 con dirección catastral) |
| `Top Ciudad`, `Top Comuna`, `Top Barrio`, `EPS Mas Frecuente` | textos para tarjetas |
| `Concentracion Comuna Top` | peso de la comuna más grande sobre Medellín (Santa Cruz, 73) |

Después de crearlas, dale formato: `% Mujeres` y `% Medellin` como **porcentaje (1 decimal)**,
`Edad Promedio` con **1 decimal**, y en `Total Personas` separador de miles.

## 5. Tema de colores

**Vista → Temas → Buscar temas** y elige **`Tema_SENA.json`**.
Colores: `#0F766E` (teal), `#39A900` (verde SENA), `#0EA5E9`, `#F59E0B`, `#EF4444`.

## 6. Páginas sugeridas del informe

### Página 1 · «Resumen»
- **6 tarjetas**: `Total Personas`, `Mujeres`, `% Mujeres`, `Edad Promedio`, `Ciudades`, `Comunas`.
- **Barras horizontales**: `DimCiudad[Ciudad]` × `Total Personas` (Top 10, orden descendente).
- **Dona**: `DimSexo[Sexo]` × `Total Personas`.
- **Barras**: `DimEPS[EPS]` × `Total Personas` (Top 10).
- **Barras**: `DimEducacion[Educacion]` × `Total Personas`.
- **Segmentador de fecha**: `HechosFicha[AnioNacimiento]` (entre).

### Página 2 · «Mapa»
- **Visual Mapa**: `Latitud` y `Longitud` (tamaño: `Total Personas`).
- **Tarjeta**: `% Medellin` y `Personas Medellin`.
- **Segmentadores**: `Sexo`, `EPS`, `Educacion`, `Comuna`.
- **Barra de rango**: `Edad` (entre 5 y 99).

### Página 3 · «Medellín»
- **Barras por comuna**: `DimComuna[Comuna]` × `Total Personas` (16 comunas).
- **Barras Top 12 barrios**: `DimBarrio[Barrio]` × `Total Personas`.
- **Mapa de burbujas**: `DimComuna[Latitud]` y `DimComuna[Longitud]`, tamaño `Total Personas`.
- **Matriz**: `Comuna` × `Sexo` con `Total Personas`.
- **Tarjetas**: `Top Comuna`, `Concentracion Comuna Top`, `Con Direccion`.

### Página 4 · «Detalle» (uso interno)
- **Tabla**: `NombreCompleto`, `TipoDoc`, `NumDoc`, `Edad`, `Ciudad`, `Comuna`,
  `BarrioMedellin`, `Telefono`, `Celular`, `EPS`, `NivelGeo`.
- Filtros de página: `Ciudad`, `Comuna`, `Sexo`.
- ⚠️ Esta página muestra datos personales: no la publiques fuera del equipo autorizado.

## 7. Que el mapa funcione

1. Vista **Modelo** → clic en `HechosFicha[Latitud]` → **Herramientas de columna →
   Categoría de datos → Latitud**.
2. Lo mismo con `HechosFicha[Longitud]` → **Longitud**.
3. En el visual de mapa, arrastra ambos campos y en el agregado elige **No resumir**
   (un punto por persona).
4. Para las comunas repite con `DimComuna[Latitud]` y `DimComuna[Longitud]`.

## 8. Ruta alternativa: CSV + Power Query

Útil si vas a actualizar los datos seguido o quieres publicarlos.

1. **Inicio → Transformar datos → Nueva consulta → Editor avanzado**.
2. Pega cada bloque de `Consultas_PowerBI.m` (uno por consulta) y ajusta la ruta.
3. **Cerrar y aplicar**.

Los CSV están en UTF-8 con separador coma y punto decimal; las fechas en formato ISO
(`AAAA-MM-DD`).

## 9. Actualizar los datos

- **Con el Excel:** reemplaza `Datos_PowerBI.xlsx` por la versión nueva (mismo nombre y
  misma ruta) y pulsa **Actualizar**.
- **Con los CSV:** reemplaza los archivos de `CSV/` y pulsa **Actualizar**.

## 10. Publicar y compartir

- **Publicar** → elige tu área de trabajo. Para actualización programada desde un archivo
  local necesitas **gateway**; si subes los CSV a SharePoint/OneDrive, Power BI actualiza
  directo con tu credencial.
- **Privacidad:** el modelo contiene documento, teléfono, correo y dirección de 666 personas.
  Si publicas, usa **seguridad a nivel de fila (RLS)** o limita el acceso al área de trabajo.
  Para una versión demostrativa, elimina las columnas `NumDoc`, `Telefono`, `Celular`,
  `Email`, `Direccion` y `NombreCompleto`.

## 11. Problemas frecuentes

| Síntoma | Solución |
|---|---|
| No aparecen las tablas al abrir el Excel | Usa «Transformar datos» y revisa que la primera fila de cada hoja tenga los encabezados. |
| No deja crear la relación `Barrio` | Debe ser `HechosFicha[BarrioMedellin]` → `DimBarrio[Barrio]` (no `Barrio`). |
| El mapa no muestra puntos | Falta la categoría de datos Latitud/Longitud o el agregado está en «Suma». |
| Los porcentajes salen en 0 % | Formatea la medida como porcentaje, no como número. |
| `Total Personas` no da 666 | Revisa las relaciones: una dimensión con duplicados multiplica filas. |
| Quiero el gráfico por barrio solo de Medellín | Filtra `Ciudad = MEDELLIN` en la página. |

## 12. Notas sobre los datos

- **666 registros** de la ficha (hoja `sheet001.htm` del archivo original).
- **287 en Medellín**: 236 con dirección catastral (`medellin.xlsx`), 45 dentro de su comuna
  y 6 solo a nivel municipal.
- **281 con comuna** (los 6 municipales no tienen comuna asignada).
- El resto del país está ubicado a nivel de municipio (379 registros) con el diccionario
  interno de 46 municipios.
- Campo `NivelGeo`: `dirección` (236), `comuna` (45), `ciudad` (6), `municipio` (379).
  Es la columna que mide la calidad de la georreferenciación.
