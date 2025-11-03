import os
import json
import math
from typing import Dict, List, Tuple
from collections import Counter
from Normalizador import normalizar_token

class ModeloEspacoVetorial:
    def __init__(self):
        self.documentos: Dict[str, Dict] = {}  # DocID -> info do documento
        self.doc_names: Dict[str, str] = {}    # DocID -> nome do arquivo
        self.indice: Dict[str, Dict[str, float]] = {}  # termo -> {DocID -> peso tf-idf}
        self.idf: Dict[str, float] = {}        # termo -> valor idf
        self.normas: Dict[str, float] = {}     # DocID -> norma do vetor
        self.carregar_indice()

    #----------------------------------------------------------------------------------------#
    def calcular_tf(self, freq: int, max_freq: int) -> float:
        #Calcula TF normalizado (0.5 + 0.5 * freq/max_freq)
        return 0.5 + 0.5 * (freq / max_freq)

    #----------------------------------------------------------------------------------------#
    def calcular_idf(self, termo: str, total_docs: int, docs_com_termo: int) -> float:
        #Calcula IDF (log(N/df))
        return math.log10(total_docs / docs_com_termo) if docs_com_termo > 0 else 0

    #----------------------------------------------------------------------------------------#
    def carregar_indice(self):
        #Carrega dados do arquivo frequencies_summary.json e calcula os pesos TF-IDF
        src_dir = os.path.dirname(__file__)
        raiz = os.path.abspath(os.path.join(src_dir, '..'))
        freq_json_path = os.path.join(raiz, 'results', 'frequencies_summary.json')

        # Novo formato simples: { "Doc.pdf": [[termo, freq], ...], ... }
        with open(freq_json_path, 'r', encoding='utf-8') as f:
            dados = json.load(f)

        # Primeiro, coleta informações básicas e calcula TF
        total_docs = len(dados)
        docs_por_termo: Dict[str, int] = Counter()  # termo -> número de docs que contém

        # Para cada documento (nome do PDF), processa suas frequências
        for pdf_nome, freq_list in dados.items():
            doc_id = pdf_nome  # usamos o nome do PDF como identificador
            # converte lista de pares em dict de frequências
            freqs = {t: int(c) for t, c in freq_list}
            self.documentos[doc_id] = {"frequencias": freqs}
            self.doc_names[doc_id] = pdf_nome

            # Encontra frequência máxima no documento para normalização do TF
            max_freq = max(freqs.values()) if freqs else 1

            # Para cada termo no documento
            for termo, freq in freqs.items():
                if termo not in self.indice:
                    self.indice[termo] = {}
                # Calcula e armazena TF normalizado
                self.indice[termo][doc_id] = self.calcular_tf(freq, max_freq)
                docs_por_termo[termo] += 1

        # Calcula IDF para cada termo
        for termo, num_docs in docs_por_termo.items():
            self.idf[termo] = self.calcular_idf(termo, total_docs, num_docs)

        # Aplica IDF aos pesos TF e calcula normas dos documentos
        for termo, docs in self.indice.items():
            idf = self.idf[termo]
            for doc_id in docs:
                self.indice[termo][doc_id] *= idf

        # Calcula norma de cada documento
        for doc_id in self.documentos:
            soma_quadrados = 0
            for termo, docs in self.indice.items():
                if doc_id in docs:
                    soma_quadrados += docs[doc_id] ** 2
            self.normas[doc_id] = math.sqrt(soma_quadrados)

    #----------------------------------------------------------------------------------------#
    def criar_vetor_consulta(self, consulta: str) -> Dict[str, float]:
        # Cria vetor TF-IDF para a consulta
        # Tokeniza, normaliza e conta frequências
        tokens_raw = consulta.split()
        if not tokens_raw:
            return {}
        
        # Normaliza cada token da mesma forma que os documentos foram normalizados
        termos_normalizados = []
        for token in tokens_raw:
            termo_norm = normalizar_token(token)
            if termo_norm:  # Ignora tokens vazios após normalização
                termos_normalizados.append(termo_norm)
        
        if not termos_normalizados:
            return {}

        # Conta frequências
        freq_consulta = Counter(termos_normalizados)
        max_freq = max(freq_consulta.values())

        # Calcula pesos TF-IDF
        pesos: Dict[str, float] = {}
        for termo, freq in freq_consulta.items():
            if termo in self.idf:  # só considera termos que existem no índice
                tf = self.calcular_tf(freq, max_freq)
                pesos[termo] = tf * self.idf[termo]

        return pesos

    #----------------------------------------------------------------------------------------#
    def similaridade_cosseno(self, vetor_consulta: Dict[str, float], doc_id: str) -> float:
        # Calcula similaridade por cosseno entre consulta e documento
        if not vetor_consulta or doc_id not in self.normas:
            return 0.0

        # Calcula produto escalar
        produto = 0.0
        for termo, peso_consulta in vetor_consulta.items():
            if termo in self.indice and doc_id in self.indice[termo]:
                produto += peso_consulta * self.indice[termo][doc_id]

        # Calcula norma do vetor de consulta
        norma_consulta = math.sqrt(sum(peso**2 for peso in vetor_consulta.values()))
        
        # Evita divisão por zero
        if norma_consulta == 0 or self.normas[doc_id] == 0:
            return 0.0

        return produto / (norma_consulta * self.normas[doc_id])

    #----------------------------------------------------------------------------------------#
    def buscar(self, consulta: str, limite: int = 10) -> List[Tuple[str, float]]:
        # Realiza busca vetorial e retorna documentos ranqueados por similaridade
        # Cria vetor para a consulta
        vetor_consulta = self.criar_vetor_consulta(consulta)
        if not vetor_consulta:
            return []

        # Calcula similaridade com cada documento
        similaridades: List[Tuple[str, float]] = []
        for doc_id in self.documentos:
            sim = self.similaridade_cosseno(vetor_consulta, doc_id)
            if sim > 0:  # só inclui documentos com alguma similaridade
                similaridades.append((doc_id, sim))

        # Ordena por similaridade (decrescente) e limita número de resultados
        similaridades.sort(key=lambda x: x[1], reverse=True)
        return similaridades[:limite]

    #----------------------------------------------------------------------------------------#
    def mostrar_resultados(self, resultados: List[Tuple[str, float]]):
        # Mostra resultados formatados
        if not resultados:
            print("\nNenhum documento encontrado.")
            return

        print(f"\nDocumentos encontrados ({len(resultados)}):")
        print("-" * 60)
        
        for i, (doc_id, similaridade) in enumerate(resultados, 1):
            nome_original = self.doc_names[doc_id]
            info = self.documentos[doc_id]
            
            print(f"{i}. {nome_original}")

#----------------------------------------------------------------------------------------#
def main():
    modelo = ModeloEspacoVetorial()
    
    print("\nBusca por Similaridade (Modelo Espaço Vetorial)")
    print("=============================================")
    print("Digite os termos da sua consulta.")
    print("Os documentos serão ranqueados por similaridade.")
    print("\nDigite 'sair' para encerrar")
    
    while True:
        try:
            consulta = input("\nConsulta: ").strip()
            if consulta.lower() == 'sair':
                break
                
            if not consulta:
                continue
                
            resultados = modelo.buscar(consulta)
            modelo.mostrar_resultados(resultados)
                
        except Exception as e:
            print(f"Erro: {e}")

#----------------------------------------------------------------------------------------#
if __name__ == "__main__":
    main()