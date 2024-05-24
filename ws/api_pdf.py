from flask import Blueprint, request, jsonify
import os
import fitz

# Generar un blueprint para la API de PDF
ws_pdf = Blueprint('ws_pdf', __name__)

# Ruta para procesar archivos PDF
@ws_pdf.route('/api/extraer', methods=['POST'])
def extract_text_from_pdf():
    # Verificar si se ha enviado un archivo PDF
    if 'pdf_file' not in request.files:
        return jsonify({'error': 'No se ha proporcionado ningún archivo PDF'}), 400

    pdf_file = request.files['pdf_file']

    # Verificar si se seleccionó un archivo
    if pdf_file.filename == '':
        return jsonify({'error': 'No se ha seleccionado ningún archivo'}), 400

    print(pdf_file)
    print("Ruta del archivo:", pdf_file.filename)
    
    # Guardar el archivo temporalmente en el servidor
    pdf_path = "temp.pdf"
    pdf_file.save(pdf_path)

    # Intentar abrir el archivo PDF
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        return jsonify({'error': f'Error al abrir el archivo PDF: {str(e)}'}), 400

    # Extraer texto de cada página del PDF
    text = ""
    for page in doc:
        text += page.get_text()

    # Cerrar el documento PDF
    doc.close()

    # Eliminar el archivo temporal después de procesarlo
    os.remove(pdf_path)

    return jsonify({'text': text}), 200
