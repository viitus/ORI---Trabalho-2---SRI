import os
import json
from typing import Set, Dict, List

class ModeloBooleano:
    def __init__(self):
        self.indice: Dict[str, Set[str]] = {}  # termo -> conjunto de DocIDs
        self.doc_ids: Dict[str, str] = {}      # nome_arquivo -> DocID
        self.doc_names: Dict[str, str] = {}    # DocID -> nome_arquivo
        self.carregar_indice()

    def carregar_indice(self):
        """Carrega o índice do arquivo frequencies_summary.json"""
        src_dir = os.path.dirname(__file__)
        raiz = os.path.abspath(os.path.join(src_dir, '..'))
        freq_json_path = os.path.join(raiz, 'results', 'frequencies_summary.json')

        with open(freq_json_path, 'r', encoding='utf-8') as f:
            dados = json.load(f)

        # Constrói índice invertido: termo -> conjunto de DocIDs
        for termo in dados["indice_geral"]:
            self.indice[termo] = set()

        # Para cada documento, adiciona seu DocID ao conjunto de cada termo que contém
        for nome_arquivo, info in dados["documentos"].items():
            doc_id = info["DocID"]
            self.doc_ids[nome_arquivo] = doc_id
            self.doc_names[doc_id] = nome_arquivo
            
            # Adiciona documento aos conjuntos dos termos que possui
            for termo, freq in info["frequencias"]:
                if freq > 0:  # redundante, mas por segurança
                    self.indice[termo].add(doc_id)

    def buscar_termo(self, termo: str) -> Set[str]:
        """Busca documentos que contêm um termo específico"""
        return self.indice.get(termo, set())

    def operador_and(self, conjunto1: Set[str], conjunto2: Set[str]) -> Set[str]:
        """Implementa o operador AND entre dois conjuntos de documentos"""
        return conjunto1 & conjunto2

    def operador_or(self, conjunto1: Set[str], conjunto2: Set[str]) -> Set[str]:
        """Implementa o operador OR entre dois conjuntos de documentos"""
        return conjunto1 | conjunto2

    def operador_not(self, conjunto: Set[str]) -> Set[str]:
        """Implementa o operador NOT para um conjunto de documentos"""
        todos_docs = set(self.doc_ids.values())
        return todos_docs - conjunto

    def processar_consulta(self, consulta: str) -> List[str]:
        """Processa uma consulta booleana e retorna a lista de documentos que correspondem"""
        # Divide a consulta em tokens
        tokens = consulta.lower().split()
        
        if not tokens:
            return []

        # Pilha para armazenar resultados intermediários
        pilha: List[Set[str]] = []
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            if token == 'not':
                # NOT deve ser seguido por um termo
                if i + 1 >= len(tokens):
                    raise ValueError("Operador NOT deve ser seguido por um termo")
                    
                # Pega o próximo termo e aplica NOT
                prox_termo = tokens[i + 1]
                resultado = self.operador_not(self.buscar_termo(prox_termo))
                pilha.append(resultado)
                i += 2
                
            elif token == 'and' or token == 'or':
                # AND/OR precisa de dois operandos
                if len(pilha) < 1 or i + 1 >= len(tokens):
                    raise ValueError(f"Operador {token.upper()} precisa de dois operandos")
                    
                op1 = pilha.pop()
                # Pega próximo termo
                prox_termo = tokens[i + 1]
                
                if prox_termo == 'not':
                    # Se próximo for NOT, processa ele primeiro
                    if i + 2 >= len(tokens):
                        raise ValueError("NOT deve ser seguido por um termo")
                    op2 = self.operador_not(self.buscar_termo(tokens[i + 2]))
                    i += 3
                else:
                    op2 = self.buscar_termo(prox_termo)
                    i += 2
                
                # Aplica o operador
                if token == 'and':
                    pilha.append(self.operador_and(op1, op2))
                else:  # OR
                    pilha.append(self.operador_or(op1, op2))
                
            else:
                # Termo normal
                pilha.append(self.buscar_termo(token))
                i += 1

        if not pilha:
            return []

        # Converte DocIDs para nomes de arquivo e remove sufixo _resumo.txt
        resultado_final = pilha[0]
        nomes_originais = []
        for doc_id in resultado_final:
            nome_txt = self.doc_names[doc_id]
            # Remove _resumo.txt do final e adiciona .pdf
            nome_original = nome_txt.replace('_resumo.txt', '.pdf')
            nomes_originais.append(nome_original)
        return sorted(nomes_originais)

def main():
    modelo = ModeloBooleano()
    
    print("\nBusca Booleana em Documentos")
    print("============================")
    print("Operadores disponíveis: AND, OR, NOT")
    print("Exemplos: ")
    print("  - termo1 AND termo2")
    print("  - termo1 OR termo2")
    print("  - termo1 AND NOT termo2")
    print("  - termo1 OR termo2 AND termo3")
    print("\nDigite 'sair' para encerrar")
    
    while True:
        try:
            consulta = input("\nConsulta: ").strip()
            if consulta.lower() == 'sair':
                break
                
            if not consulta:
                continue
                
            resultados = modelo.processar_consulta(consulta)
            
            print(f"\nDocumentos PDF encontrados ({len(resultados)}):")
            if resultados:
                for i, doc in enumerate(resultados, 1):
                    print(f"{i}. {doc}")
            else:
                print("Nenhum documento encontrado.")
                
        except ValueError as e:
            print(f"Erro na consulta: {e}")
        except Exception as e:
            print(f"Erro inesperado: {e}")

if __name__ == "__main__":
    main()
