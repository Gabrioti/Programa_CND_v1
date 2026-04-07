# main.py

import sys
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

# Importa o cérebro que criamos no processador.py
from processador import processar_todas_cnds

class RedirecionadorPrint:
    def __init__(self, widget_texto): 
        self.widget_texto = widget_texto
    def write(self, texto):
        self.widget_texto.insert(tk.END, texto)
        self.widget_texto.see(tk.END)
        self.widget_texto.update_idletasks()
    def flush(self): pass

def selecionar_pasta():
    pasta = filedialog.askdirectory(title="Selecione a pasta com os PDFs")
    if pasta:
        label_caminho.config(text=pasta)
        btn_processar.config(state=tk.NORMAL)

def iniciar_processamento():
    btn_processar.config(state=tk.DISABLED)
    caixa_texto.delete(1.0, tk.END)
    
    # Chama a função principal de processamento importada
    processar_todas_cnds(label_caminho.cget("text"))
    
    messagebox.showinfo("Concluído", "Todos os PDFs foram processados com sucesso!")
    btn_processar.config(state=tk.NORMAL)

# Cria a Janela
janela = tk.Tk()
janela.title("Leitor e Renomeador de CNDs")
janela.geometry("600x500")
janela.configure(padx=20, pady=20)

tk.Label(janela, text="Automação de CNDs", font=("Arial", 16, "bold")).pack(pady=(0, 10))
tk.Button(janela, text="📁 Selecionar Pasta", command=selecionar_pasta, font=("Arial", 12), width=20).pack(pady=5)
label_caminho = tk.Label(janela, text="Nenhuma pasta selecionada", fg="blue", font=("Arial", 9))
label_caminho.pack(pady=5)
btn_processar = tk.Button(janela, text="▶ Iniciar Processamento", command=iniciar_processamento, font=("Arial", 12, "bold"), bg="green", fg="white", state=tk.DISABLED, width=20)
btn_processar.pack(pady=15)
tk.Label(janela, text="Progresso:", font=("Arial", 10, "bold")).pack(anchor="w")

caixa_texto = scrolledtext.ScrolledText(janela, width=70, height=15, bg="black", fg="lightgreen", font=("Consolas", 9))
caixa_texto.pack(fill=tk.BOTH, expand=True)

sys.stdout = RedirecionadorPrint(caixa_texto)

if __name__ == "__main__":
    janela.mainloop()