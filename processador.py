# processador.py

import os
import re
from datetime import datetime, timedelta
import pdfplumber
from tkinter import simpledialog, messagebox

from regras import identificar_cnd
from leitor_ocr import extrair_texto_com_ocr

def processar_todas_cnds(pasta_trabalho, modo_debug=False):
    arquivos_pdf = [arquivo for arquivo in os.listdir(pasta_trabalho) if arquivo.lower().endswith('.pdf')]
    if not arquivos_pdf:
        print("\n[!] Nenhum arquivo PDF encontrado nesta pasta.")
        return

    print(f"\nIniciando AUTO-DETECÇÃO em {len(arquivos_pdf)} arquivo(s) PDF...")

    for nome_arquivo in arquivos_pdf:
        caminho_atual = os.path.join(pasta_trabalho, nome_arquivo)
        print(f"\n{'-'*50}\nLendo: {nome_arquivo}")
        
        status, data_atualizacao, data_encontrada = "Indefinido", "00.00.00", None
        origem, numero_categoria, cidade = None, None, "" 
        
        try:
            with pdfplumber.open(caminho_atual) as pdf:
                primeira_pagina = pdf.pages[0]
                texto_do_pdf = primeira_pagina.extract_text()

                #TRANSFORMA TUDO EM MAIÚSCULO
                if texto_do_pdf:
                    texto_do_pdf = texto_do_pdf.upper()
                
                letras_normais = len(re.findall(r'[A-Z]', texto_do_pdf)) if texto_do_pdf else 0
                if not texto_do_pdf or len(texto_do_pdf.strip()) < 20 or letras_normais < 20:
                    texto_do_pdf = extrair_texto_com_ocr(caminho_atual)

            # ==========================================
            # O TRUQUE DO MODO DEBUG FICA AQUI
            # ==========================================
            if modo_debug:
                print(f"\n[🔎 MODO DEBUG ATIVADO] O que o robô leu no arquivo {nome_arquivo}:")
                print("========================================")
                print(texto_do_pdf)
                print("========================================\n")

            origem, numero_categoria = identificar_cnd(texto_do_pdf)
            if not origem:
                print("-> AVISO: Órgão não identificado. Pulando...")
                continue
            
            if not modo_debug:
                print(f"-> Identificado: CND {origem}")

            # REGRAS DE LEITURA
            if origem == "Federal":
                if "EFEITO DE NEGATIVA" in texto_do_pdf or "EFEITOS DE NEGATIVA" in texto_do_pdf: status = "Positiva com Efeito Negativo"
                elif "NEGATIVA" in texto_do_pdf or "NÃO CONSTA" in texto_do_pdf or "NAO CONSTA" in texto_do_pdf: status = "Negativa"
                elif "POSITIVA" in texto_do_pdf or "CONSTA" in texto_do_pdf: status = "Positiva"
                busca_validade = re.search(r'V[ÁA]LIDA AT[ÉE]\s*(\d{2}/\d{2}/\d{4})', texto_do_pdf)
                if busca_validade: data_encontrada = busca_validade.group(1)

            elif origem == "Estadual":
                if "EFEITO DE NEGATIVA" in texto_do_pdf or "EFEITOS DE NEGATIVA" in texto_do_pdf: status = "Positiva com Efeito Negativo"
                elif "NEGATIVA" in texto_do_pdf or "NAO CONSTA DEBITO" in texto_do_pdf: status = "Negativa"
                elif "POSITIVA" in texto_do_pdf or "CONSTA DEBITO" in texto_do_pdf: status = "Positiva"
                dias_validade = 60
                busca_dias = re.search(r'VALIDA POR\s+(\d+)\s+DIAS', texto_do_pdf)
                if busca_dias: dias_validade = int(busca_dias.group(1))
                busca_emissao = re.search(r'(\d{1,2})\s+([A-ZÇ]+)\s+DE\s+(\d{4})', texto_do_pdf)
                if busca_emissao:
                    dia, mes_texto, ano = int(busca_emissao.group(1)), busca_emissao.group(2).replace("Ç", "C"), int(busca_emissao.group(3))
                    meses = {"JANEIRO": 1, "FEVEREIRO": 2, "MARCO": 3, "ABRIL": 4, "MAIO": 5, "JUNHO": 6, "JULHO": 7, "AGOSTO": 8, "SETEMBRO": 9, "OUTUBRO": 10, "NOVEMBRO": 11, "DEZEMBRO": 12}
                    if meses.get(mes_texto):
                        try: data_encontrada = (datetime(ano, meses[mes_texto], dia) + timedelta(days=dias_validade)).strftime("%d/%m/%Y")
                        except: pass

            elif origem == "Municipal":
                busca_nome_cidade = re.search(r'(?:PREFEITURA MUNICIPAL DE|MUNIC[ÍI]PIO DE)\s+([A-ZÁÀÂÃÉÈÊÍÏÓÒÔÕÚÙÛÇ ]+)', texto_do_pdf)
                busca_alt = re.search(r'ADMINISTRADOS PELA\s+([A-ZÁÀÂÃÉÈÊÍÏÓÒÔÕÚÙÛÇ ]+?)(?:\s+-|\s*,)', texto_do_pdf)
                
                if busca_nome_cidade:
                    cidade = re.sub(r'(?i)\s+DE\s+GOI[ÁA]S$', '', busca_nome_cidade.group(1).split('\n')[0].strip()).title()
                elif busca_alt:
                    cidade = re.sub(r'(?i)\s+DE\s+GOI[ÁA]S$', '', busca_alt.group(1).strip()).title()
                else:
                    resposta = simpledialog.askstring("Cidade não identificada", f"Arquivo: {nome_arquivo}\nPor favor, digite o nome da cidade:")
                    cidade = resposta.strip().title() if resposta else "Desconhecida"

                if "EFEITO DE NEGATIVA" in texto_do_pdf or "EFEITOS DE NEGATIVA" in texto_do_pdf or "EFEITO NEGATIVO" in texto_do_pdf or "EFEITO NEGATIVA": status = "Positiva com Efeito Negativo"
                elif "NEGATIVA" in texto_do_pdf or "NÃO CONSTA" in texto_do_pdf or "NAO CONSTA" in texto_do_pdf: status = "Negativa"
                elif "POSITIVA" in texto_do_pdf: status = "Positiva"
                
                busca_emissao = re.search(r'VALIDADE[^\d]*(\d{1,2})\s+(?:DE\s+)?([A-ZÇ]+)\s+(?:DE\s+)?(\d{4})', texto_do_pdf)
                if busca_emissao:
                    dia, mes_texto, ano = int(busca_emissao.group(1)), busca_emissao.group(2).replace("Ç", "C"), int(busca_emissao.group(3))
                    meses = {"JANEIRO": 1, "FEVEREIRO": 2, "MARCO": 3, "ABRIL": 4, "MAIO": 5, "JUNHO": 6, "JULHO": 7, "AGOSTO": 8, "SETEMBRO": 9, "OUTUBRO": 10, "NOVEMBRO": 11, "DEZEMBRO": 12}
                    if meses.get(mes_texto):
                        try: data_encontrada = datetime(ano, meses[mes_texto], dia).strftime("%d/%m/%Y")
                        except: pass
                
                if not data_encontrada:
                    busca_validade_barras = re.search(r'(?:V[ÁA]LIDA AT[ÉE]|VALIDADE).*?(\d{2}/\d{2}/\d{4})', texto_do_pdf)
                    if busca_validade_barras: data_encontrada = busca_validade_barras.group(1)

            elif origem == "Trabalhista":
                if "EFEITO DE NEGATIVA" in texto_do_pdf or "EFEITOS DE NEGATIVA" in texto_do_pdf: status = "Positiva com Efeito Negativo"
                elif "CERTIDÃO NEGATIVA" in texto_do_pdf or "NÃO CONSTA COMO INADIMPLENTE" in texto_do_pdf: status = "Negativa"
                elif "CERTIDÃO POSITIVA" in texto_do_pdf: status = "Positiva"
                busca_validade = re.search(r'VALIDADE:\s*(\d{2}/\d{2}/\d{4})', texto_do_pdf)
                if busca_validade: data_encontrada = busca_validade.group(1)

            elif origem == "Comprasnet":
                if "EFEITO DE NEGATIVA" in texto_do_pdf or "EFEITOS DE NEGATIVA" in texto_do_pdf: status = "Positiva com Efeito Negativo"
                elif "CERTIDÃO - NEGATIVA" in texto_do_pdf or "NÃO CONSTA REGISTRO" in texto_do_pdf: status = "Negativa"
                elif "CERTIDÃO - POSITIVA" in texto_do_pdf: status = "Positiva"
                
                busca_dias = re.search(r'VÁLIDA POR\s+(\d+)\s+DIAS', texto_do_pdf)
                dias_validade = int(busca_dias.group(1)) if busca_dias else 30
                
                busca_emissao = re.search(r'DATA DE EMISSÃO:\s*(\d{2}[./]\d{2}[./]\d{2,4})', texto_do_pdf)
                if busca_emissao:
                    data_emissao_str = busca_emissao.group(1).replace(".", "/") 
                    try:
                        formato = "%d/%m/%Y" if len(data_emissao_str) == 10 else "%d/%m/%y"
                        data_encontrada = (datetime.strptime(data_emissao_str, formato) + timedelta(days=dias_validade)).strftime("%d/%m/%Y")
                    except: data_encontrada = data_emissao_str

            elif origem == "FGTS":
                if re.search(r'EFEITOS?\s+DE\s+NEGATIVA', texto_do_pdf): 
                    status = "Positiva com Efeito Negativo"
                elif re.search(r'SITUA[ÇC][ÃA]O\s+REGULAR', texto_do_pdf) or "REGULAR PERANTE O FUNDO" in texto_do_pdf: 
                    status = "Negativa" 
                else: 
                    status = "Positiva"
                
                busca_data = re.search(r'VALIDADE.*?\d{2}[./]\d{2}[./]\d{2,4}[^\d]+(\d{2}[./]\d{2}[./]\d{2,4})', texto_do_pdf)
                if busca_data: data_encontrada = busca_data.group(1)

            elif origem == "AGEHAB":
                if "EFEITO DE NEGATIVA" in texto_do_pdf or "EFEITOS DE NEGATIVA" in texto_do_pdf: status = "Positiva com Efeito Negativo"
                elif "NEGATIVA" in texto_do_pdf: status = "Negativa"
                elif "POSITIVA" in texto_do_pdf: status = "Positiva"
                busca_validade = re.search(r'V[ÁA]LIDA AT[ÉE][^\d]*(\d{2}/\d{2}/\d{4})', texto_do_pdf)
                if busca_validade: data_encontrada = busca_validade.group(1)

            if not data_encontrada:
                busca_data_solta = re.search(r'\d{2}[./]\d{2}[./]\d{2,4}', texto_do_pdf)
                if busca_data_solta: data_encontrada = busca_data_solta.group()

            if data_encontrada:
                partes = data_encontrada.replace("/", ".").split(".")
                if len(partes) == 3: data_atualizacao = f"{partes[0]}.{partes[1]}.{partes[2][-2:]}"
                else: data_atualizacao = data_encontrada.replace("/", ".")

        except Exception as e:
            print(f"Erro ao ler arquivo: {e}")
            continue

        nome_origem = cidade if origem == "Municipal" and cidade else origem
        nome_base = f"{numero_categoria} - CND {nome_origem} - {status} - {data_atualizacao}"
        nome_final = f"{nome_base}.pdf"
        caminho_final = os.path.join(pasta_trabalho, nome_final)
        
        if caminho_atual == caminho_final:
            if not modo_debug:
                print(f"-> O arquivo já está perfeitamente atualizado: '{nome_final}' (Nenhuma mudança necessária).")
            continue

        contador = 1
        while os.path.exists(caminho_final):
            nome_final = f"{nome_base} ({contador}).pdf"
            caminho_final = os.path.join(pasta_trabalho, nome_final)
            contador += 1
        
        try:
            os.rename(caminho_atual, caminho_final)
            if not modo_debug:
                print(f"-> SUCESSO! Renomeado para: '{nome_final}'")
        except Exception as e: print(f"-> ERRO ao renomear: {e}")

    print(f"\n{'-'*50}\nAutomação concluída!")
    try:
        messagebox.showinfo("Concluído", "Processamento finalizado!")
    except: pass
