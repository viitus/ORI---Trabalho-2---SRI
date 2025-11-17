import os
import json
from typing import Set, Dict, List
from Normalizador import normalizar_token

class ModeloBooleano:
    def __init__(self):
        self.indice: Dict[str, Set[str]] = {}  # termo -> conjunto de DocIDs
        self.doc_ids: Dict[str, str] = {}      # nome_arquivo -> DocID
        self.doc_names: Dict[str, str] = {}    # DocID -> nome_arquivo
        self.carregar_indice()

    #----------------------------------------------------------------------------------------#
    def carregar_indice(self):
        # Carrega o índice do arquivo frequencies_summary.json
        src_dir = os.path.dirname(__file__)
        raiz = os.path.abspath(os.path.join(src_dir, '..'))
        freq_json_path = os.path.join(raiz, 'results', 'frequencies_summary.json')
        # Novo formato simples esperado: { "Doc.pdf": [[termo, frequencia], ...], ... }
        with open(freq_json_path, 'r', encoding='utf-8') as f:
            dados = json.load(f)

        # Constrói índice invertido: termo -> conjunto de document names (PDF)
        for pdf_nome, freq_list in dados.items():
            # Usamos o nome do PDF como o identificador do documento (doc_id)
            doc_id = pdf_nome if pdf_nome.endswith('.pdf') else f"{pdf_nome}.pdf"
            self.doc_ids[pdf_nome] = doc_id
            self.doc_names[doc_id] = pdf_nome

            for termo, freq in freq_list:
                if termo not in self.indice:
                    self.indice[termo] = set()
                if freq > 0:
                    self.indice[termo].add(doc_id)

    #----------------------------------------------------------------------------------------#
    def buscar_termo(self, termo: str) -> Set[str]:
        # Busca documentos que contêm um termo específico
        # Normaliza o termo da mesma forma que os documentos foram normalizados
        termo_normalizado = normalizar_token(termo)
        return self.indice.get(termo_normalizado, set())

    #----------------------------------------------------------------------------------------#
    def operador_and(self, conjunto1: Set[str], conjunto2: Set[str]) -> Set[str]:
        # Implementa o operador AND entre dois conjuntos de documentos
        return conjunto1 & conjunto2

    #----------------------------------------------------------------------------------------#
    def operador_or(self, conjunto1: Set[str], conjunto2: Set[str]) -> Set[str]:
        # Implementa o operador OR entre dois conjuntos de documentos
        return conjunto1 | conjunto2

    #----------------------------------------------------------------------------------------#
    def operador_not(self, conjunto: Set[str]) -> Set[str]:
        # Implementa o operador NOT para um conjunto de documentos
        todos_docs = set(self.doc_ids.values())
        return todos_docs - conjunto

    #----------------------------------------------------------------------------------------#
    def processar_consulta(self, consulta: str) -> List[str]:
        # Processa uma consulta booleana e retorna a lista de documentos que correspondem
        # Divide a consulta em tokens (não precisa lowercase aqui, normalizar_token já faz isso)
        tokens = consulta.split()
        
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
                
            elif token.lower() == 'and' or token.lower() == 'or':
                # AND/OR precisa de dois operandos
                if len(pilha) < 1 or i + 1 >= len(tokens):
                    raise ValueError(f"Operador {token.upper()} precisa de dois operandos")
                    
                op1 = pilha.pop()
                # Pega próximo termo
                prox_termo = tokens[i + 1]
                
                if prox_termo.lower() == 'not':
                    # Se próximo for NOT, processa ele primeiro
                    if i + 2 >= len(tokens):
                        raise ValueError("NOT deve ser seguido por um termo")
                    op2 = self.operador_not(self.buscar_termo(tokens[i + 2]))
                    i += 3
                else:
                    op2 = self.buscar_termo(prox_termo)
                    i += 2
                    # Aplica o operador
                if token.lower() == 'and':
                    pilha.append(self.operador_and(op1, op2))
                else:  # OR
                    pilha.append(self.operador_or(op1, op2))
                
            else:
                # Termo normal
                pilha.append(self.buscar_termo(token))
                i += 1

        if not pilha:
            return []
        return sorted(list(pilha[0]))

#----------------------------------------------------------------------------------------#
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

#----------------------------------------------------------------------------------------#
if __name__ == "__main__":
    main()
