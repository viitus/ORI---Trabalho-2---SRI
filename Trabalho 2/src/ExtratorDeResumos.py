import os
from PyPDF2 import PdfReader

def extrair_resumos():
    # Caminho para a pasta docs (um nível acima da pasta src)
    pasta_docs = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs')
    
    # Caminho para a pasta results (um nível acima da pasta src)
    pasta_results = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')

    # Pasta específica para resumos
    pasta_resumo = os.path.join(pasta_results, 'resumo')

    # Cria as pastas results/resumo se não existirem
    os.makedirs(pasta_resumo, exist_ok=True)
    
    # Lista para armazenar os resumos
    resumos = []
    
    # Verifica se a pasta existe
    if not os.path.exists(pasta_docs):
        print(f"A pasta {pasta_docs} não foi encontrada!")
        return []
    
    # Lista todos os arquivos PDF na pasta docs
    for arquivo in os.listdir(pasta_docs):
        if arquivo.lower().endswith('.pdf'):
            caminho_completo = os.path.join(pasta_docs, arquivo)
            try:
                # Abre o arquivo PDF
                with open(caminho_completo, 'rb') as arquivo_pdf:
                    # Cria um leitor PDF
                    leitor = PdfReader(arquivo_pdf)
                    
                    # Extrai o texto das primeiras páginas até ter pelo menos 1000 palavras
                    texto_completo = ""
                    for pagina in leitor.pages:
                        texto_completo += pagina.extract_text() + " "
                        if len(texto_completo.split()) >= 1000:
                            break

                    # Procura a palavra "RESUMO" (case insensitive)
                    texto_lower = texto_completo.lower()
                    indice_resumo = texto_lower.find('resumo')
                    
                    if indice_resumo != -1:
                        # Pega a posição onde encontrou "RESUMO"
                        inicio = indice_resumo + len('resumo')
                        
                        # Pega o texto após "RESUMO"
                        texto_apos_resumo = texto_completo[inicio:]

                        # Pega as próximas 300 palavras
                        palavras = texto_apos_resumo.split()
                        if len(palavras) > 300:
                            palavras = palavras[:300]
                        resumo = ' '.join(palavras)
                        
                        # Cria o nome do arquivo de saída dentro de results/resumo
                        nome_arquivo_saida = os.path.splitext(arquivo)[0] + '_resumo.txt'
                        caminho_saida = os.path.join(pasta_resumo, nome_arquivo_saida)

                        # Salva o resumo em um arquivo txt dentro de results/resumo
                        with open(caminho_saida, 'w', encoding='utf-8') as f:
                            f.write(resumo)
                        
                        resumos.append({
                            'nome_arquivo': arquivo,
                            'texto': resumo
                        })
                        print(f"Resumo extraído com sucesso do arquivo {arquivo}!")
                    else:
                        print(f"Palavra 'RESUMO' não encontrada no arquivo {arquivo}")
                    
            except Exception as e:
                print(f"Erro ao processar o arquivo {arquivo}: {str(e)}")
    
    return resumos

if __name__ == "__main__":
    print("Iniciando extração de resumos...")
    resumos = extrair_resumos()
    print(f"\nTotal de resumos extraídos: {len(resumos)}")