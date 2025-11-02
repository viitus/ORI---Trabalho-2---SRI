import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import scrolledtext
import os
import subprocess
from ModeloBooleano import ModeloBooleano
from ModeloEspacoVetorial import ModeloEspacoVetorial
from ExtratorDeResumos import ExtratorDeResumos, extrair_resumos
from Normalizador import processar_pasta_results
from pathlib import Path
from Reiniciar import apagar_conteudo


class SistemaBuscaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Busca em Documentos")
        self.root.geometry("800x600")
        
        # Guarda o caminho da pasta docs
        self.pasta_docs = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'docs'
        )

        # Inicializa os modelos
        try:
            self.modelo_booleano = ModeloBooleano()
            self.modelo_vetorial = ModeloEspacoVetorial()
            self.modelos_carregados = True
        except Exception as e:
            self.modelos_carregados = False
            tk.messagebox.showerror("Erro", f"Erro ao carregar modelos: {str(e)}")

        # Cria notebook para as abas
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)

        # Cria as três abas
        self.tab_booleana = ttk.Frame(self.notebook)
        self.tab_vetorial = ttk.Frame(self.notebook)
        self.tab_arquivos = ttk.Frame(self.notebook)

        # Adiciona as abas ao notebook
        self.notebook.add(self.tab_booleana, text='Busca Booleana')
        self.notebook.add(self.tab_vetorial, text='Busca Vetorial')
        self.notebook.add(self.tab_arquivos, text='Lista de Arquivos')

        # Configura cada aba
        self.configurar_aba_booleana()
        self.configurar_aba_vetorial()
        self.configurar_aba_arquivos()

    def configurar_aba_booleana(self):
        # Frame para a consulta
        frame_consulta = ttk.Frame(self.tab_booleana)
        frame_consulta.pack(fill='x', padx=10, pady=5)

        # Label e entrada para a consulta
        ttk.Label(frame_consulta, text="Consulta:").pack(side='left', padx=(0,5))
        self.entrada_booleana = ttk.Entry(frame_consulta)
        self.entrada_booleana.pack(side='left', fill='x', expand=True)
        
        # Botão de busca
        ttk.Button(frame_consulta, text="Buscar", 
                  command=self.realizar_busca_booleana).pack(side='left', padx=(5,0))

        # Área de instruções
        frame_instrucoes = ttk.Frame(self.tab_booleana)
        frame_instrucoes.pack(fill='x', padx=10, pady=5)
        ttk.Label(frame_instrucoes, 
                 text="Operadores: AND, OR, NOT\nExemplos: termo1 AND termo2, termo1 OR NOT termo2",
                 justify='left').pack(anchor='w')

        # Área de resultados
        frame_resultados = ttk.Frame(self.tab_booleana)
        frame_resultados.pack(fill='both', expand=True, padx=10, pady=5)
        
        ttk.Label(frame_resultados, text="Resultados:").pack(anchor='w')
        self.resultados_booleana = scrolledtext.ScrolledText(frame_resultados, height=20)
        self.resultados_booleana.pack(fill='both', expand=True)

    def configurar_aba_vetorial(self):
        # Frame para a consulta
        frame_consulta = ttk.Frame(self.tab_vetorial)
        frame_consulta.pack(fill='x', padx=10, pady=5)

        # Label e entrada para a consulta
        ttk.Label(frame_consulta, text="Consulta:").pack(side='left', padx=(0,5))
        self.entrada_vetorial = ttk.Entry(frame_consulta)
        self.entrada_vetorial.pack(side='left', fill='x', expand=True)
        
        # Botão de busca
        ttk.Button(frame_consulta, text="Buscar", 
                  command=self.realizar_busca_vetorial).pack(side='left', padx=(5,0))

        # Área de instruções
        frame_instrucoes = ttk.Frame(self.tab_vetorial)
        frame_instrucoes.pack(fill='x', padx=10, pady=5)
        ttk.Label(frame_instrucoes, 
                 text="Digite os termos da consulta separados por espaço.\nOs resultados serão ordenados por relevância.",
                 justify='left').pack(anchor='w')

        # Área de resultados
        frame_resultados = ttk.Frame(self.tab_vetorial)
        frame_resultados.pack(fill='both', expand=True, padx=10, pady=5)
        
        ttk.Label(frame_resultados, text="Resultados:").pack(anchor='w')
        self.resultados_vetorial = scrolledtext.ScrolledText(frame_resultados, height=20)
        self.resultados_vetorial.pack(fill='both', expand=True)

    def configurar_aba_arquivos(self):
        # Frame para lista de arquivos
        frame_lista = ttk.Frame(self.tab_arquivos)
        frame_lista.pack(fill='both', expand=True, padx=10, pady=5)

        ttk.Label(frame_lista, text="Documentos Disponíveis:").pack(anchor='w')
        self.lista_arquivos = scrolledtext.ScrolledText(frame_lista, height=25)
        self.lista_arquivos.pack(fill='both', expand=True)

        # Frame para botões de arquivo
        frame_botoes_arquivo = ttk.Frame(self.tab_arquivos)
        frame_botoes_arquivo.pack(fill='x', padx=10, pady=5)

        # Botões para gerenciar arquivos
        ttk.Button(frame_botoes_arquivo, text="Atualizar Lista", 
                  command=self.atualizar_lista_arquivos).pack(side='left', padx=5)
        ttk.Button(frame_botoes_arquivo, text="Abrir Pasta", 
                  command=self.abrir_pasta_docs).pack(side='left', padx=5)

        # Frame para botões de processamento
        frame_botoes_proc = ttk.Frame(self.tab_arquivos)
        frame_botoes_proc.pack(fill='x', padx=10, pady=5)

        # Botões para processamento
        ttk.Button(frame_botoes_proc, text="Extrair e Normalizar", 
                  command=self.extrair_e_normalizar).pack(side='left', padx=5)
        ttk.Button(frame_botoes_proc, text="Reiniciar Sistema", 
                  command=self.reiniciar_sistema).pack(side='left', padx=5)

        # Carrega lista inicial
        self.atualizar_lista_arquivos()

    def realizar_busca_booleana(self):
        if not self.modelos_carregados:
            self.resultados_booleana.delete(1.0, tk.END)
            self.resultados_booleana.insert(tk.END, "Erro: Modelos não carregados corretamente.")
            return

        consulta = self.entrada_booleana.get().strip()
        if not consulta:
            return

        try:
            resultados = self.modelo_booleano.processar_consulta(consulta)
            
            self.resultados_booleana.delete(1.0, tk.END)
            if resultados:
                self.resultados_booleana.insert(tk.END, f"Documentos encontrados ({len(resultados)}):\n\n")
                for i, doc in enumerate(resultados, 1):
                    self.resultados_booleana.insert(tk.END, f"{i}. {doc}\n\n")
            else:
                self.resultados_booleana.insert(tk.END, "Nenhum documento encontrado.")
        except Exception as e:
            self.resultados_booleana.delete(1.0, tk.END)
            self.resultados_booleana.insert(tk.END, f"Erro na consulta: {str(e)}")

    def realizar_busca_vetorial(self):
        if not self.modelos_carregados:
            self.resultados_vetorial.delete(1.0, tk.END)
            self.resultados_vetorial.insert(tk.END, "Erro: Modelos não carregados corretamente.")
            return

        consulta = self.entrada_vetorial.get().strip()
        if not consulta:
            return

        try:
            resultados = self.modelo_vetorial.buscar(consulta)
            
            self.resultados_vetorial.delete(1.0, tk.END)
            if resultados:
                self.resultados_vetorial.insert(tk.END, f"Documentos encontrados ({len(resultados)}):\n\n")
                for i, (doc_id, similaridade) in enumerate(resultados, 1):
                    nome_doc = self.modelo_vetorial.doc_names[doc_id]
                    info = self.modelo_vetorial.documentos[doc_id]
                    self.resultados_vetorial.insert(tk.END, 
                        f"{i}. {nome_doc}\n\n")
            else:
                self.resultados_vetorial.insert(tk.END, "Nenhum documento encontrado.")
        except Exception as e:
            self.resultados_vetorial.delete(1.0, tk.END)
            self.resultados_vetorial.insert(tk.END, f"Erro na consulta: {str(e)}")

    def abrir_pasta_docs(self):
        """Abre a pasta docs no Windows Explorer"""
        if os.path.exists(self.pasta_docs):
            os.startfile(self.pasta_docs)
        else:
            tk.messagebox.showerror("Erro", "Pasta 'docs/' não encontrada!")

    def extrair_e_normalizar(self):
        """Executa a extração e normalização dos documentos"""
        try:
            # 1) Extrai resumos para results/resumo/
            extrator = ExtratorDeResumos()
            resultado_extracao = extrator.processar_documentos()

            # 2) Normaliza os arquivos de resumo gerados
            processar_pasta_results()

            messagebox.showinfo("Sucesso", f"Extração concluída ({len(resultado_extracao)} arquivos) e normalização finalizada.")
            # Atualiza lista e tenta recarregar modelos
            self.atualizar_lista_arquivos()
            try:
                self.modelo_booleano = ModeloBooleano()
                self.modelo_vetorial = ModeloEspacoVetorial()
                self.modelos_carregados = True
            except Exception as e:
                self.modelos_carregados = False
                messagebox.showwarning("Aviso", f"Extraído e normalizado, mas erro ao recarregar modelos: {e}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar documentos: {str(e)}")

    def reiniciar_sistema(self):
        """Reinicia o sistema, limpando e recriando os arquivos necessários"""
        try:
            # Confirma com o usuário
            if not messagebox.askyesno("Confirmar", 
                "Isso irá limpar todos os dados processados (pastas results e data). Continuar?"):
                return

            # Usa a função apagar_conteudo do Reiniciar.py para limpeza segura e recursiva
            src_dir = os.path.dirname(__file__)
            base_dir = os.path.dirname(src_dir)

            results_path = Path(base_dir) / 'results'
            data_path = Path(base_dir) / 'data'

            resumo_msgs = []

            if results_path.exists():
                files, dirs = apagar_conteudo(results_path)
                resumo_msgs.append(f"results: {files} arquivos, {dirs} pastas removidos")
            else:
                resumo_msgs.append("results: pasta não encontrada")

            if data_path.exists():
                files2, dirs2 = apagar_conteudo(data_path)
                resumo_msgs.append(f"data: {files2} arquivos, {dirs2} pastas removidos")
            else:
                resumo_msgs.append("data: pasta não encontrada")

            messagebox.showinfo("Sucesso", "Sistema reiniciado com sucesso!\n" + "\n".join(resumo_msgs))

            # Recarrega a interface
            self.atualizar_lista_arquivos()
            self.modelos_carregados = False

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao reiniciar sistema: {str(e)}")

    def atualizar_lista_arquivos(self):
        try:
            self.lista_arquivos.delete(1.0, tk.END)
            
            if not os.path.exists(self.pasta_docs):
                self.lista_arquivos.insert(tk.END, "Pasta 'docs/' não encontrada.")
                return
                
            arquivos = [f for f in os.listdir(self.pasta_docs) if f.lower().endswith('.pdf')]
            
            if not arquivos:
                self.lista_arquivos.insert(tk.END, "Nenhum arquivo PDF encontrado.")
                return
                
            self.lista_arquivos.insert(tk.END, f"Total de documentos: {len(arquivos)}\n\n")
            for i, arquivo in enumerate(sorted(arquivos), 1):
                caminho = os.path.join(self.pasta_docs, arquivo)
                tamanho = os.path.getsize(caminho) / 1024  # KB
                self.lista_arquivos.insert(tk.END, f"{i}. {arquivo}\n   Tamanho: {tamanho:.1f} KB\n\n")
                
        except Exception as e:
            self.lista_arquivos.delete(1.0, tk.END)
            self.lista_arquivos.insert(tk.END, f"Erro ao listar arquivos: {str(e)}")

def main():
    root = tk.Tk()
    app = SistemaBuscaGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
