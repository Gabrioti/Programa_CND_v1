# leitor_ocr.py

import sys
import os
import pytesseract
from pdf2image import convert_from_path

def obter_pasta_base():
    """Retorna a pasta onde este script ou o executável está salvo"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def extrair_texto_com_ocr(caminho_pdf):
    print("-> Fonte corrompida! Acionando OCR...")
    texto_extraido = ""
    
    pasta_base = obter_pasta_base()
    
    # O código procura as ferramentas na pasta "Motores", junto do script ou do .exe
    caminho_tesseract = os.path.join(pasta_base, 'Motores', 'tesseract.exe')
    caminho_poppler = os.path.join(pasta_base, 'Motores', 'poppler-25.12.0', 'Library', 'bin')
    pasta_tessdata = os.path.join(pasta_base, 'Motores', 'tessdata')
    
    pytesseract.pytesseract.tesseract_cmd = caminho_tesseract
    os.environ["TESSDATA_PREFIX"] = pasta_tessdata

    try:
        imagens = convert_from_path(caminho_pdf, poppler_path=caminho_poppler) 
        for imagem in imagens:
            texto = pytesseract.image_to_string(imagem, lang='por')
            texto_extraido += texto + "\n"
        return texto_extraido.upper()
    except Exception as e:
        print(f"Erro no OCR: {e}")
        return ""