import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter import scrolledtext
import os
import shutil
import json
from ModeloBooleano import ModeloBooleano
from ModeloEspacoVetorial import ModeloEspacoVetorial
from ExtratorDeResumos import ExtratorDeResumos
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
        self.pasta_data = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data'
        )
        os.makedirs(self.pasta_data, exist_ok=True)

        # Inicializa os modelos
        self.recarregar_modelos()

        # Cria notebook para as abas
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)

        # Cria as três abas
        self.tab_booleana = ttk.Frame(self.notebook)
        self.tab_vetorial = ttk.Frame(self.notebook)
        self.tab_arquivos = ttk.Frame(self.notebook)
        self.tab_cadastro = ttk.Frame(self.notebook)

        # Adiciona as abas ao notebook
        self.notebook.add(self.tab_booleana, text='Busca Booleana')
        self.notebook.add(self.tab_vetorial, text='Busca Vetorial')
        self.notebook.add(self.tab_cadastro, text='Cadastrar Documento')
        self.notebook.add(self.tab_arquivos, text='Lista de Arquivos')

        # Configura cada aba
        self.configurar_aba_booleana()
        self.configurar_aba_vetorial()
        self.configurar_aba_arquivos()
        self.configurar_aba_cadastro()

    #----------------------------------------------------------------------------------------#
    def configurar_aba_booleana(self):
        # Frame para a consulta
        frame_consulta = ttk.Frame(self.tab_booleana)
        frame_consulta.pack(fill='x', padx=10, pady=5)

        # Label e entrada para a consulta
        ttk.Label(frame_consulta, text="Consulta:").pack(side='left', padx=(0,5))
        self.entrada_booleana = ttk.Entry(frame_consulta)
        self.entrada_booleana.pack(side='left', fill='x', expand=True)
        
        # Botão de busca
        ttk.Button(frame_consulta, text="Buscar", command=self.realizar_busca_booleana).pack(side='left', padx=(5,0))

        # Área de instruções
        frame_instrucoes = ttk.Frame(self.tab_booleana)
        frame_instrucoes.pack(fill='x', padx=10, pady=5)
        ttk.Label(frame_instrucoes, text="Operadores: AND, OR, NOT\nExemplos: termo1 AND termo2, termo1 OR NOT termo2",justify='left').pack(anchor='w')

        # Área de resultados
        frame_resultados = ttk.Frame(self.tab_booleana)
        frame_resultados.pack(fill='both', expand=True, padx=10, pady=5)
        
        ttk.Label(frame_resultados, text="Resultados:").pack(anchor='w')
        
        # Usar Treeview para resultados
        self.tree_booleana = ttk.Treeview(frame_resultados, columns=("documento",), show="headings", height=10)
        self.tree_booleana.heading("documento", text="Documento Encontrado")
        self.tree_booleana.column("documento", anchor='w')

        # Adicionar scrollbar
        scrollbar_booleana = ttk.Scrollbar(frame_resultados, orient="vertical", command=self.tree_booleana.yview)
        self.tree_booleana.configure(yscrollcommand=scrollbar_booleana.set)

        self.tree_booleana.pack(side='left', fill='both', expand=True)
        scrollbar_booleana.pack(side='right', fill='y')

        self.tree_booleana.bind("<Double-1>", self.exibir_metadados)


    #----------------------------------------------------------------------------------------#
    def configurar_aba_vetorial(self):
        # Frame para a consulta
        frame_consulta = ttk.Frame(self.tab_vetorial)
        frame_consulta.pack(fill='x', padx=10, pady=5)

        # Label e entrada para a consulta
        ttk.Label(frame_consulta, text="Consulta:").pack(side='left', padx=(0,5))
        self.entrada_vetorial = ttk.Entry(frame_consulta)
        self.entrada_vetorial.pack(side='left', fill='x', expand=True)
        
        # Botão de busca
        ttk.Button(frame_consulta, text="Buscar", command=self.realizar_busca_vetorial).pack(side='left', padx=(5,0))

        # Área de instruções
        frame_instrucoes = ttk.Frame(self.tab_vetorial)
        frame_instrucoes.pack(fill='x', padx=10, pady=5)
        ttk.Label(frame_instrucoes, text="Digite os termos da consulta separados por espaço.\nOs resultados serão ordenados por relevância.", justify='left').pack(anchor='w')

        # Área de resultados
        frame_resultados = ttk.Frame(self.tab_vetorial)
        frame_resultados.pack(fill='both', expand=True, padx=10, pady=5)
        
        ttk.Label(frame_resultados, text="Resultados:").pack(anchor='w')

        # Usar Treeview para resultados
        self.tree_vetorial = ttk.Treeview(frame_resultados, columns=("documento", "similaridade"), show="headings", height=10)
        self.tree_vetorial.heading("documento", text="Documento")
        self.tree_vetorial.heading("similaridade", text="Similaridade")
        self.tree_vetorial.column("documento", anchor='w', width=400)
        self.tree_vetorial.column("similaridade", anchor='center', width=100)

        # Adicionar scrollbar
        scrollbar_vetorial = ttk.Scrollbar(frame_resultados, orient="vertical", command=self.tree_vetorial.yview)
        self.tree_vetorial.configure(yscrollcommand=scrollbar_vetorial.set)

        self.tree_vetorial.pack(side='left', fill='both', expand=True)
        scrollbar_vetorial.pack(side='right', fill='y')

        self.tree_vetorial.bind("<Double-1>", self.exibir_metadados)

    #----------------------------------------------------------------------------------------#
    def configurar_aba_arquivos(self):
        # Frame para lista de arquivos
        frame_lista = ttk.Frame(self.tab_arquivos)
        frame_lista.pack(fill='both', expand=True, padx=10, pady=5)

        ttk.Label(frame_lista, text="Documentos Disponíveis:").pack(anchor='w')

        # Usar Treeview para a lista de documentos — torna itens clicáveis e fáceis de exibir metadados
        self.tree_lista = ttk.Treeview(frame_lista, columns=("documento",), show="headings", height=15)
        self.tree_lista.heading("documento", text="Documento")
        self.tree_lista.column("documento", anchor='w')

        scrollbar_lista = ttk.Scrollbar(frame_lista, orient="vertical", command=self.tree_lista.yview)
        self.tree_lista.configure(yscrollcommand=scrollbar_lista.set)

        self.tree_lista.pack(side='left', fill='both', expand=True)
        scrollbar_lista.pack(side='right', fill='y')

        # Duplo clique em um documento mostra metadados e resumo
        self.tree_lista.bind("<Double-1>", self.exibir_metadados)

        # Frame para botões
        frame_botoes = ttk.Frame(self.tab_arquivos)
        frame_botoes.pack(fill='x', padx=10, pady=5)

        # Botões para gerenciar documentos
        ttk.Button(frame_botoes, text="Abrir Pasta", command=self.abrir_pasta_docs).pack(side='left', padx=5)
        ttk.Button(frame_botoes, text="Atualizar Documentos", command=self.atualizar_documentos_novos).pack(side='left', padx=5)
        ttk.Button(frame_botoes, text="Reiniciar e Extrair", command=self.reiniciar_e_extrair).pack(side='left', padx=5)

        # Carrega lista inicial
        self.atualizar_lista_arquivos()

    #----------------------------------------------------------------------------------------#
    def configurar_aba_cadastro(self):
        frame_cadastro = ttk.Frame(self.tab_cadastro)
        frame_cadastro.pack(fill='both', expand=True, padx=10, pady=5)

        # Campos de entrada
        campos = ["Título:", "Autor(es):", "Filiação acadêmica:", "Palavras-chave:"]
        self.entradas_cadastro = {}

        for i, campo in enumerate(campos):
            ttk.Label(frame_cadastro, text=campo).grid(row=i, column=0, sticky='w', padx=5, pady=2)
            entry = ttk.Entry(frame_cadastro, width=80)
            entry.grid(row=i, column=1, sticky='ew', padx=5, pady=2)
            self.entradas_cadastro[campo[:-1]] = entry

        # Seleção de arquivo PDF
        row_pdf = len(campos)
        ttk.Label(frame_cadastro, text="Arquivo PDF:").grid(row=row_pdf, column=0, sticky='w', padx=5, pady=2)
        
        frame_pdf = ttk.Frame(frame_cadastro)
        frame_pdf.grid(row=row_pdf, column=1, sticky='ew')
        
        self.caminho_pdf_selecionado = tk.StringVar()
        ttk.Button(frame_pdf, text="Selecionar PDF...", command=self.selecionar_pdf).pack(side='left')
        ttk.Label(frame_pdf, textvariable=self.caminho_pdf_selecionado, wraplength=400).pack(side='left', padx=5)

        # Botão Salvar
        ttk.Button(frame_cadastro, text="Salvar Documento", command=self.salvar_documento).grid(row=row_pdf + 1, column=1, sticky='e', padx=5, pady=10)

        frame_cadastro.columnconfigure(1, weight=1)

    #----------------------------------------------------------------------------------------#
    def selecionar_pdf(self):
        caminho = filedialog.askopenfilename(
            title="Selecione o arquivo PDF",
            filetypes=[("Arquivos PDF", "*.pdf")]
        )
        if caminho:
            self.caminho_pdf_selecionado.set(caminho)

    #----------------------------------------------------------------------------------------#
    def salvar_documento(self):
        caminho_pdf_origem = self.caminho_pdf_selecionado.get()
        if not caminho_pdf_origem:
            messagebox.showerror("Erro", "Por favor, selecione um arquivo PDF.")
            return

        try:
            # Não copiar para docs: o usuário preferiu não sobrescrever arquivos.
            # Salvamos apenas as informações do formulário em um JSON em 'data'.
            nome_pdf = os.path.basename(caminho_pdf_origem)
            metadata = {k: v.get() for k, v in self.entradas_cadastro.items()}

            # Guardar caminho original do PDF no metadado para referência
            metadata['arquivo_original'] = caminho_pdf_origem

            base_nome = os.path.splitext(nome_pdf)[0]
            nome_metadata_json = f"{base_nome}_metadata.json"
            with open(os.path.join(self.pasta_data, nome_metadata_json), 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=4)

            messagebox.showinfo("Sucesso", f"Metadados salvos em: {nome_metadata_json}")

        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Ocorreu um erro: {e}")

    #----------------------------------------------------------------------------------------#
    def recarregar_modelos(self):
        """Libera os modelos existentes e carrega os novos a partir dos arquivos de índice."""
        self.modelo_booleano = None
        self.modelo_vetorial = None
        self.modelos_carregados = False
        try:
            self.modelo_booleano = ModeloBooleano()
            self.modelo_vetorial = ModeloEspacoVetorial()
            self.modelos_carregados = True
            print("Modelos recarregados com sucesso.")
        except FileNotFoundError:
            self.modelos_carregados = False
            print("Arquivos de índice não encontrados. Modelos não foram carregados.")
        except Exception as e:
            self.modelos_carregados = False
            messagebox.showerror("Erro ao Recarregar Modelos", f"Ocorreu um erro: {str(e)}")
    #----------------------------------------------------------------------------------------#
    def exibir_metadados(self, event):
        # Pega o item selecionado da árvore que disparou o evento
        tree = event.widget
        if not tree.selection():
            return
        
        item_selecionado = tree.selection()[0]
        # O nome do documento está na primeira coluna ('values[0]')
        nome_doc = tree.item(item_selecionado, "values")[0]

        # Só processa entradas que parecem nomes de PDF
        if not nome_doc.lower().endswith('.pdf'):
            # Pode ser a linha informativa (ex: Total de documentos). Ignorar.
            return

        base_nome = os.path.splitext(nome_doc)[0]
        caminho_metadata = os.path.join(self.pasta_data, f"{base_nome}_metadata.json")
        caminho_resumo = os.path.join(os.path.dirname(self.pasta_docs), 'results', 'resumo', f"{base_nome}_resumo.txt")
        caminho_pdf = os.path.join(self.pasta_docs, nome_doc)

        metadata = {}
        # Carrega metadados do JSON, se existir
        if os.path.exists(caminho_metadata):
            try:
                with open(caminho_metadata, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            except Exception as e:
                messagebox.showwarning("Aviso", f"Não foi possível ler os metadados de '{nome_doc}': {e}")

        # Carrega o resumo, se existir
        if os.path.exists(caminho_resumo):
            try:
                with open(caminho_resumo, 'r', encoding='utf-8') as f:
                    metadata['Resumo'] = f.read()
            except Exception as e:
                messagebox.showwarning("Aviso", f"Não foi possível ler o resumo de '{nome_doc}': {e}")
        else:
             metadata.setdefault('Resumo', 'Não encontrado.')

        # Cria uma nova janela (Toplevel) para exibir os metadados
        janela_meta = tk.Toplevel(self.root)
        janela_meta.title(f"Detalhes - {nome_doc}")
        janela_meta.geometry("700x500")

        frame_meta = ttk.Frame(janela_meta, padding="10")
        frame_meta.pack(fill='both', expand=True)

        # Exibe os metadados
        row = 0
        for chave, valor in metadata.items():
            ttk.Label(frame_meta, text=f"{chave}:", font=("Helvetica", 10, "bold")).grid(row=row, column=0, sticky='nw', pady=2)
            
            # Define uma altura maior para o campo de resumo
            height = 10 if chave == 'Resumo' else 2
            
            text_widget = scrolledtext.ScrolledText(frame_meta, height=height, wrap=tk.WORD, relief="flat", background=janela_meta.cget('bg'))
            text_widget.insert(tk.END, valor)
            
            # Ajusta a altura dinamicamente, especialmente para campos que não são o resumo
            if chave != 'Resumo':
                text_widget.config(height=min(8, valor.count('\n') + (len(valor) // 70) + 2))
            
            text_widget.config(state='disabled')
            text_widget.grid(row=row, column=1, sticky='ew', pady=2, padx=5)
            row += 1
        
        frame_meta.columnconfigure(1, weight=1)

        # Botão para abrir o PDF
        if os.path.exists(caminho_pdf):
            ttk.Button(frame_meta, text="Abrir PDF", command=lambda: os.startfile(caminho_pdf)).grid(row=row, column=1, sticky='e', pady=10)

    #----------------------------------------------------------------------------------------#
    def realizar_busca_booleana(self):
        if not self.modelos_carregados:
            messagebox.showerror("Erro", "Modelos não carregados corretamente. Tente reiniciar o sistema.")
            return

        consulta = self.entrada_booleana.get().strip()
        if not consulta:
            return

        # Limpa resultados anteriores
        for i in self.tree_booleana.get_children():
            self.tree_booleana.delete(i)

        try:
            resultados = self.modelo_booleano.processar_consulta(consulta)
            
            if resultados:
                for doc in resultados:
                    self.tree_booleana.insert("", "end", values=(doc,))
            else:
                messagebox.showinfo("Busca Booleana", "Nenhum documento encontrado para a consulta.")
        except Exception as e:
            messagebox.showerror("Erro na Consulta", f"Erro na consulta: {str(e)}")

    #----------------------------------------------------------------------------------------#
    def realizar_busca_vetorial(self):
        if not self.modelos_carregados:
            messagebox.showerror("Erro", "Modelos não carregados corretamente. Tente reiniciar o sistema.")
            return

        consulta = self.entrada_vetorial.get().strip()
        if not consulta:
            return

        # Limpa resultados anteriores
        for i in self.tree_vetorial.get_children():
            self.tree_vetorial.delete(i)

        try:
            resultados = self.modelo_vetorial.buscar(consulta)
            if resultados:
                for doc_id, similaridade in resultados:
                    nome_doc = self.modelo_vetorial.doc_names[doc_id]
                    self.tree_vetorial.insert("", "end", values=(nome_doc, f"{similaridade:.4f}"))
            else:
                messagebox.showinfo("Busca Vetorial", "Nenhum documento encontrado para a consulta.")
        except Exception as e:
            messagebox.showerror("Erro na Consulta", f"Erro na consulta: {str(e)}")

    #----------------------------------------------------------------------------------------#
    def abrir_pasta_docs(self):
        # Abre a pasta docs no Windows Explorer
        if os.path.exists(self.pasta_docs):
            os.startfile(self.pasta_docs)
        else:
            tk.messagebox.showerror("Erro", "Pasta 'docs/' não encontrada!")
    
    #----------------------------------------------------------------------------------------#
    def extrair_e_normalizar(self, arquivos_para_processar: list = None):
        # Executa a extração e normalização dos documentos
        """try:
            # Extrai resumos para results/resumo/
            extrator = ExtratorDeResumos()
            resultado_extracao = extrator.processar_documentos()

            # Normaliza os arquivos de resumo gerados
            processar_pasta_results()

            messagebox.showinfo("Sucesso", f"Extração concluída ({len(resultado_extracao)} arquivos) e normalização finalizada.")
            # Atualiza lista e tenta recarregar modelos
            self.recarregar_modelos()
            self.atualizar_lista_arquivos()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar documentos: {str(e)}")
        """
        try:
            # Extrai resumos para os arquivos especificados (ou todos se None)
            extrator = ExtratorDeResumos()
            resultado_extracao = extrator.processar_documentos(arquivos_para_processar)

            # Se estamos processando arquivos específicos, precisamos passar os nomes dos resumos para o normalizador
            if arquivos_para_processar:
                nomes_resumos = [os.path.splitext(f)[0] + '_resumo.txt' for f in arquivos_para_processar]
                processar_pasta_results(apenas_novos=nomes_resumos)
            else: # Processamento completo
                processar_pasta_results()

            # Monta a mensagem de sucesso
            if arquivos_para_processar:
                msg = f"Atualização concluída. {len(resultado_extracao)} novo(s) arquivo(s) processado(s) e adicionado(s) ao índice."
            else:
                msg = f"Extração completa concluída ({len(resultado_extracao)} arquivos) e normalização finalizada."

            messagebox.showinfo("Sucesso", msg)
            
            # Libera modelos antigos e recarrega com os novos dados
            self.recarregar_modelos()
            self.atualizar_lista_arquivos()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar documentos: {str(e)}")

    #----------------------------------------------------------------------------------------#
    def atualizar_documentos_novos(self):
        # Esta função foi substituída pela lógica dentro de `reiniciar_e_extrair` e `atualizar_documentos_novos`
        # A função `extrair_e_normalizar` agora lida com ambos os casos.
        pass
    #----------------------------------------------------------------------------------------#
    def reiniciar_e_extrair(self):
        # Reinicia o sistema, limpa os arquivos e executa extração/normalização
        try:
            # Confirma com o usuário
            if not messagebox.askyesno("Reiniciar Sistema", 
                "Tem certeza que deseja reiniciar?\n\nEsta ação irá apagar todos os dados existentes (índices, resumos, metadados) e recriá-los a partir dos documentos na pasta 'docs'."):
                return

            # Libera os modelos para evitar erro de arquivo em uso no Windows
            self.modelo_booleano = None
            self.modelo_vetorial = None
            self.modelos_carregados = False
            for i in self.tree_booleana.get_children():
                self.tree_booleana.delete(i)
            for i in self.tree_vetorial.get_children():
                self.tree_vetorial.delete(i)
            # Usa a função apagar_conteudo do Reiniciar.py para limpeza segura e recursiva
            results_path = Path(os.path.dirname(self.pasta_docs)) / 'results'
            data_path = Path(self.pasta_data)

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

            # Executa extração e normalização após limpar
            try:
                extrator = ExtratorDeResumos()
                self.extrair_e_normalizar() # Chama a função que agora faz tudo
                
                # Tenta recarregar os modelos
                self.recarregar_modelos()
                
                msg_sucesso = "Sistema reiniciado e dados reprocessados!\n"
                msg_sucesso += "\n".join(resumo_msgs)
                # A mensagem de sucesso agora é mostrada dentro de extrair_e_normalizar
                
                messagebox.showinfo("Sucesso", msg_sucesso)
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao processar documentos: {str(e)}")
                self.modelos_carregados = False
            
            # Atualiza a lista de arquivos
            self.atualizar_lista_arquivos()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao reiniciar sistema: {str(e)}")

    #----------------------------------------------------------------------------------------#
    def atualizar_documentos_novos(self):
        """Verifica se há novos arquivos na pasta 'docs' e os processa."""
        try:
            # 1. Obter lista de arquivos PDF na pasta 'docs'
            pdfs_na_pasta = {f for f in os.listdir(self.pasta_docs) if f.lower().endswith('.pdf')}

            # 2. Obter lista de arquivos já processados (chaves do modelo vetorial são os nomes dos PDFs)
            if not self.modelos_carregados:
                # Se os modelos não estiverem carregados, processa tudo
                messagebox.showinfo("Informação", "Nenhum índice carregado. Processando todos os documentos.")
                self.extrair_e_normalizar()
                return
            
            pdfs_processados = set(self.modelo_vetorial.doc_names.values())

            # 3. Encontrar a diferença
            novos_arquivos = list(pdfs_na_pasta - pdfs_processados)

            if not novos_arquivos:
                messagebox.showinfo("Atualizar Documentos", "Nenhum documento novo encontrado.")
                return

            # 4. Confirmar com o usuário e processar os novos arquivos
            msg_confirmacao = "Os seguintes novos arquivos foram encontrados:\n\n" + "\n".join(novos_arquivos) + "\n\nDeseja processá-los e adicioná-los ao índice?"
            if messagebox.askyesno("Novos Documentos Encontrados", msg_confirmacao):
                self.extrair_e_normalizar(arquivos_para_processar=novos_arquivos)

        except Exception as e:
            messagebox.showerror("Erro ao Atualizar", f"Ocorreu um erro ao verificar novos documentos: {str(e)}")




    #----------------------------------------------------------------------------------------#
    def atualizar_lista_arquivos(self):
        try:
            # Clear TreeView
            for iid in self.tree_lista.get_children():
                self.tree_lista.delete(iid)
            
            if not os.path.exists(self.pasta_docs):
                self.tree_lista.insert("", "end", values=("Pasta 'docs/' não encontrada.",))
                return
                
            arquivos = [f for f in os.listdir(self.pasta_docs) if f.lower().endswith('.pdf')]
            
            if not arquivos:
                self.tree_lista.insert("", "end", values=("Nenhum arquivo PDF encontrado.",))
                return
                
            self.tree_lista.insert("", "end", values=(f"Total de documentos: {len(arquivos)}",))
            for i, arquivo in enumerate(sorted(arquivos), 1):
                self.tree_lista.insert("", "end", values=(arquivo,))
                
        except Exception as e:
            for iid in self.tree_lista.get_children():
                self.tree_lista.delete(iid)
            self.tree_lista.insert("", "end", values=(f"Erro ao listar arquivos: {str(e)}",))

#----------------------------------------------------------------------------------------#
def main():
    root = tk.Tk()
    app = SistemaBuscaGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
