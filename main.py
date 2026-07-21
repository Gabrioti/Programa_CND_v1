# main.py

import os
import sys
import subprocess

if os.name == 'nt':  # Verifica se o sistema é Windows
    CREATE_NO_WINDOW = 0x08000000
    original_popen = subprocess.Popen

    # Cria uma versão modificada que esconde a janela à força
    def popen_sem_janela(*args, **kwargs):
        kwargs['creationflags'] = CREATE_NO_WINDOW
        return original_popen(*args, **kwargs)

    # Substitui a função padrão do Python pela nossa versão invisível
    subprocess.Popen = popen_sem_janela


import tkinter as tk
from tkinter import filedialog, scrolledtext

from processador import processar_todas_cnds

class RedirecionadorPrint:
    def __init__(self, widget_texto): 
        self.widget_texto = widget_texto
    def write(self, texto):
        self.widget_texto.insert(tk.END, texto)
        self.widget_texto.see(tk.END)
        self.widget_texto.update_idletasks()
    def flush(self): pass

def mostrar_tutorial():
    """Esconde a tela principal e mostra a tela de ajuda."""
    frame_principal.pack_forget()
    frame_tutorial.pack(fill=tk.BOTH, expand=True)

def voltar_principal():
    """Esconde a tela de ajuda e volta para o programa."""
    frame_tutorial.pack_forget()
    frame_principal.pack(fill=tk.BOTH, expand=True)

def selecionar_pasta():
    pasta = filedialog.askdirectory(title="Selecione a pasta com os PDFs")
    if pasta:
        label_caminho.config(text=pasta)
        btn_processar.config(state=tk.NORMAL)

def iniciar_processamento():
    btn_processar.config(state=tk.DISABLED)
    caixa_texto.delete(1.0, tk.END)
    
    # Verifica se a caixinha de Debug está marcada
    debug_ativado = var_debug.get()
    
    processar_todas_cnds(label_caminho.cget("text"), debug_ativado)
    btn_processar.config(state=tk.NORMAL)

# ==========================================
# CONFIGURAÇÃO DA JANELA PRINCIPAL
# ==========================================
janela = tk.Tk()
janela.title("Leitor e Renomeador de CNDs")
janela.geometry("650x550")
janela.configure(padx=20, pady=20)

# Criando as duas "Páginas" (Frames)
frame_principal = tk.Frame(janela)
frame_tutorial = tk.Frame(janela)

# ==========================================
# TELA 1: FRAME PRINCIPAL (Onde o programa roda)
# ==========================================
# Título e Botão de Ajuda na mesma linha (usando um mini-frame invisível)
frame_topo = tk.Frame(frame_principal)
frame_topo.pack(fill=tk.X, pady=(0, 10))

tk.Label(frame_topo, text="Automação de CNDs", font=("Arial", 16, "bold")).pack(side=tk.LEFT, expand=True)
btn_ajuda = tk.Button(frame_topo, text="❔ Como Usar", command=mostrar_tutorial, fg="blue", cursor="hand2")
btn_ajuda.pack(side=tk.RIGHT)

# Botões e Textos do Programa
tk.Button(frame_principal, text="📂 Selecionar Pasta", command=selecionar_pasta, font=("Arial", 12), width=20).pack(pady=5)
label_caminho = tk.Label(frame_principal, text="Nenhuma pasta selecionada", fg="blue", font=("Arial", 9))
label_caminho.pack(pady=5)

btn_processar = tk.Button(frame_principal, text="▶ Iniciar Processamento", command=iniciar_processamento, font=("Arial", 12, "bold"), bg="green", fg="white", state=tk.DISABLED, width=20)
btn_processar.pack(pady=10)

var_debug = tk.BooleanVar()
chk_debug = tk.Checkbutton(frame_principal, text="🔍 MODO DEBUG (Mostrar texto extraído dos PDFs)", variable=var_debug, font=("Arial", 10), fg="red")
chk_debug.pack(pady=5)

tk.Label(frame_principal, text="Progresso e Logs:", font=("Arial", 10, "bold")).pack(anchor="w")
caixa_texto = scrolledtext.ScrolledText(frame_principal, width=70, height=15, bg="black", fg="lightgreen", font=("Consolas", 9))
caixa_texto.pack(fill=tk.BOTH, expand=True)

# ==========================================
# TELA 2: FRAME DE TUTORIAL (Fica escondido no começo)
# ==========================================
tk.Label(frame_tutorial, text="📖 Como usar a Automação", font=("Arial", 16, "bold")).pack(pady=(0, 20))

instrucoes = """
1. Clique em 'Selecionar Pasta' e escolha onde estão os PDFs originais.

2. Certifique-se de que a pasta contém apenas os PDFs de CNDs 
   que você deseja renomear.

3. Clique em 'Iniciar Processamento'. 

4. O robô vai ler cada PDF invisivelmente, extrair o CNPJ, a data 
   de validade e o status, e renomear o arquivo na mesma pasta.

DICA: Se quiser ver exatamente o que o robô está lendo (útil para 
arquivos com erro), marque a caixinha 'MODO DEBUG' antes de iniciar.
"""

tk.Label(frame_tutorial, text=instrucoes, font=("Arial", 11), justify=tk.LEFT, bg="#f0f0f0", padx=15, pady=15).pack(fill=tk.X)

btn_voltar = tk.Button(frame_tutorial, text="⬅ Voltar ao Programa", command=voltar_principal, font=("Arial", 11, "bold"), bg="gray", fg="white", cursor="hand2")
btn_voltar.pack(pady=20)

# ==========================================
# INICIALIZAÇÃO
# ==========================================
# Avisa o programa para mostrar o Frame Principal primeiro
frame_principal.pack(fill=tk.BOTH, expand=True)


# ==========================================
# ASSINATURA DO CRIADOR
# ==========================================
lbl_creditos = tk.Label(janela, text="Desenvolvido por: [Felipe Andrade Gabrioti/AGEHAB] © 2026", font=("Arial", 8, "italic"), fg="gray")
lbl_creditos.pack(side=tk.BOTTOM, pady=5)

sys.stdout = RedirecionadorPrint(caixa_texto)

# Inicializa o programa mostrando apenas a tela principal
frame_principal.pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    janela.mainloop()