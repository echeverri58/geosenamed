// Consultas de Power Query para el modelo de la Ficha del Ciudadano
// Uso: Power BI → Inicio → Transformar datos → Nueva consulta → Editor avanzado,
// pega cada bloque (uno por consulta) y ajusta la variable Ruta.

// Tabla: Hechos_Ficha
let
    Ruta = "C:\Users\ASUS vivobook\Desktop\Gereferenciacion de datos\PowerBI\CSV",
    Origen = Csv.Document(File.Contents(Ruta & "\Hechos_Ficha.csv"),
        [Delimiter = ",", Columns = 36, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Encabezados = Table.PromoteHeaders(Origen, [PromoteAllScalars = true]),
    Tipos = Table.TransformColumnTypes(Encabezados,
        {{"ID", type text}, {"Linea", type text}, {"FechaCreacion", type date}, {"FechaActualizacion", type date}, {"TipoDoc", type text}, {"NumDoc", type text}, {"NombreCompleto", type text}, {"PrimerNombre", type text}, {"SegundoNombre", type text}, {"PrimerApellido", type text}, {"SegundoApellido", type text}, {"FechaNacimiento", type date}, {"AnioNacimiento", Int64.Type}, {"Decada", type text}, {"Edad", Int64.Type}, {"Sexo", type text}, {"Direccion", type text}, {"Barrio", type text}, {"BarrioMedellin", type text}, {"Comuna", type text}, {"Ciudad", type text}, {"Departamento", type text}, {"Latitud", type number}, {"Longitud", type number}, {"NivelGeo", type text}, {"FuenteGeo", type text}, {"MedellinAsignado", type text}, {"Institucion", type text}, {"Cobertura", type text}, {"EPS", type text}, {"EstadoCivil", type text}, {"Educacion", type text}, {"Ocupacion", type text}, {"Telefono", type text}, {"Celular", type text}, {"Email", type text}})
in
    Tipos


// Tabla: Dim_Ciudad
let
    Ruta = "C:\Users\ASUS vivobook\Desktop\Gereferenciacion de datos\PowerBI\CSV",
    Origen = Csv.Document(File.Contents(Ruta & "\Dim_Ciudad.csv"),
        [Delimiter = ",", Columns = 6, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Encabezados = Table.PromoteHeaders(Origen, [PromoteAllScalars = true]),
    Tipos = Table.TransformColumnTypes(Encabezados,
        {{"Ciudad", type text}, {"Departamento", type text}, {"Latitud", type number}, {"Longitud", type number}, {"Registros", Int64.Type}, {"EsMedellin", type text}})
in
    Tipos


// Tabla: Dim_Comuna
let
    Ruta = "C:\Users\ASUS vivobook\Desktop\Gereferenciacion de datos\PowerBI\CSV",
    Origen = Csv.Document(File.Contents(Ruta & "\Dim_Comuna.csv"),
        [Delimiter = ",", Columns = 5, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Encabezados = Table.PromoteHeaders(Origen, [PromoteAllScalars = true]),
    Tipos = Table.TransformColumnTypes(Encabezados,
        {{"Numero", Int64.Type}, {"Comuna", type text}, {"Registros", Int64.Type}, {"Latitud", type number}, {"Longitud", type number}})
in
    Tipos


// Tabla: Dim_Barrio
let
    Ruta = "C:\Users\ASUS vivobook\Desktop\Gereferenciacion de datos\PowerBI\CSV",
    Origen = Csv.Document(File.Contents(Ruta & "\Dim_Barrio.csv"),
        [Delimiter = ",", Columns = 3, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Encabezados = Table.PromoteHeaders(Origen, [PromoteAllScalars = true]),
    Tipos = Table.TransformColumnTypes(Encabezados,
        {{"Barrio", type text}, {"Comuna", type text}, {"Registros", Int64.Type}})
in
    Tipos


// Tabla: Dim_EPS
let
    Ruta = "C:\Users\ASUS vivobook\Desktop\Gereferenciacion de datos\PowerBI\CSV",
    Origen = Csv.Document(File.Contents(Ruta & "\Dim_EPS.csv"),
        [Delimiter = ",", Columns = 2, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Encabezados = Table.PromoteHeaders(Origen, [PromoteAllScalars = true]),
    Tipos = Table.TransformColumnTypes(Encabezados,
        {{"EPS", type text}, {"Registros", Int64.Type}})
in
    Tipos


// Tabla: Dim_Educacion
let
    Ruta = "C:\Users\ASUS vivobook\Desktop\Gereferenciacion de datos\PowerBI\CSV",
    Origen = Csv.Document(File.Contents(Ruta & "\Dim_Educacion.csv"),
        [Delimiter = ",", Columns = 2, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Encabezados = Table.PromoteHeaders(Origen, [PromoteAllScalars = true]),
    Tipos = Table.TransformColumnTypes(Encabezados,
        {{"Educacion", type text}, {"Registros", Int64.Type}})
in
    Tipos


// Tabla: Dim_Sexo
let
    Ruta = "C:\Users\ASUS vivobook\Desktop\Gereferenciacion de datos\PowerBI\CSV",
    Origen = Csv.Document(File.Contents(Ruta & "\Dim_Sexo.csv"),
        [Delimiter = ",", Columns = 2, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Encabezados = Table.PromoteHeaders(Origen, [PromoteAllScalars = true]),
    Tipos = Table.TransformColumnTypes(Encabezados,
        {{"Sexo", type text}, {"Registros", Int64.Type}})
in
    Tipos


// Tabla: Dim_Institucion
let
    Ruta = "C:\Users\ASUS vivobook\Desktop\Gereferenciacion de datos\PowerBI\CSV",
    Origen = Csv.Document(File.Contents(Ruta & "\Dim_Institucion.csv"),
        [Delimiter = ",", Columns = 2, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Encabezados = Table.PromoteHeaders(Origen, [PromoteAllScalars = true]),
    Tipos = Table.TransformColumnTypes(Encabezados,
        {{"Institucion", type text}, {"Registros", Int64.Type}})
in
    Tipos


// Tabla: Dim_Cobertura
let
    Ruta = "C:\Users\ASUS vivobook\Desktop\Gereferenciacion de datos\PowerBI\CSV",
    Origen = Csv.Document(File.Contents(Ruta & "\Dim_Cobertura.csv"),
        [Delimiter = ",", Columns = 2, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Encabezados = Table.PromoteHeaders(Origen, [PromoteAllScalars = true]),
    Tipos = Table.TransformColumnTypes(Encabezados,
        {{"Cobertura", type text}, {"Registros", Int64.Type}})
in
    Tipos
