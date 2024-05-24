from flask import Blueprint, request, jsonify
import os
import fitz
import tempfile

# Generar un blueprint para la API de PDF
ws_prueba = Blueprint('ws_prueba', __name__)

# Función para extraer texto entre dos páginas específicas
def extraer_texto_entre_paginas(doc, pagina_inicio, pagina_fin, titulo_inicio, titulo_fin):
    texto_total = ""
    for pagina_num in range(pagina_inicio, pagina_fin + 1):
        pagina_obj = doc.load_page(pagina_num - 1)  # Las páginas en PyMuPDF son 0-indexadas
        texto = pagina_obj.get_text("text")
        if pagina_num == pagina_inicio:
            # Encontrar el inicio del subtítulo
            inicio = texto.find(titulo_inicio)
            if inicio != -1:
                texto = texto[inicio + len(titulo_inicio):]
        if pagina_num == pagina_fin and titulo_fin:
            # Encontrar el inicio del siguiente subtítulo
            fin = texto.find(titulo_fin)
            if fin != -1:
                texto = texto[:fin]
        texto_total += texto.strip() + " "
    return texto_total.strip()

# Ruta para procesar archivos PDF
@ws_prueba.route('/api/prueba', methods=['POST'])
def extract_text_from_pdf():
    # Verificar si se ha enviado un archivo PDF
    if 'pdf_file' not in request.files:
        return jsonify({'error': 'No se ha proporcionado ningún archivo PDF'}), 400

    pdf_file = request.files['pdf_file']

    # Verificar si se seleccionó un archivo
    if pdf_file.filename == '':
        return jsonify({'error': 'No se ha seleccionado ningún archivo'}), 400

    # Guardar el archivo temporalmente en el servidor
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        pdf_path = temp_file.name
        pdf_file.save(pdf_path)

    # Intentar abrir el archivo PDF
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        # Asegurar que el archivo temporal sea eliminado en caso de error
        os.remove(pdf_path)
        return jsonify({'error': f'Error al abrir el archivo PDF: {str(e)}'}), 400

    # Inicializar una lista para almacenar los textos de cada subtítulo
    subtitulos_texto = []

    try:
        # Obtener la tabla de contenido
        tabla_contenido = doc.get_toc()

        # Iterar sobre la tabla de contenido
        for i, entry in enumerate(tabla_contenido):
            title = entry[1]
            page_number = entry[2]
            level = entry[0]

            if level == 2:  # Subtítulo
                # Determinar el inicio del siguiente subtítulo o título principal
                if i + 1 < len(tabla_contenido):
                    next_entry = tabla_contenido[i + 1]
                    next_title = next_entry[1]
                    next_page_number = next_entry[2]
                else:
                    next_title = None
                    next_page_number = doc.page_count

                # Extraer el texto entre el subtítulo actual y el siguiente
                texto = extraer_texto_entre_paginas(doc, page_number, next_page_number, title, next_title)
                subtitulos_texto.append({'title': title, 'text': texto})
    finally:
        # Cerrar el documento PDF y eliminar el archivo temporal
        doc.close()
        os.remove(pdf_path)

    # Devolver los textos de cada subtítulo como una lista
    return jsonify({'subtitulos_texto': subtitulos_texto}), 200