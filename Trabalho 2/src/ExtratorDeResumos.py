import os
import logging
from typing import List, Dict
from PyPDF2 import PdfReader

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')


class ExtratorDeResumos:
    def __init__(self, pasta_docs: str = None, pasta_results: str = None,
                 max_palavras_texto: int = 1000, max_palavras_resumo: int = 300):
        src_dir = os.path.dirname(__file__)
        raiz = os.path.abspath(os.path.join(src_dir, '..'))
        self.pasta_docs = pasta_docs or os.path.join(raiz, 'docs')
        self.pasta_results = pasta_results or os.path.join(raiz, 'results')
        self.pasta_resumo = os.path.join(self.pasta_results, 'resumo')
        self.max_palavras_texto = max_palavras_texto
        self.max_palavras_resumo = max_palavras_resumo
        
        # Número de palavras a usar como fallback quando não for encontrado o marcador 'RESUMO'
        self.fallback_palavras = 500

        os.makedirs(self.pasta_resumo, exist_ok=True)

    def _extrair_texto_pdf(self, caminho_pdf: str) -> str:
        texto_completo = ""
        try:
            with open(caminho_pdf, 'rb') as f:
                leitor = PdfReader(f)
                for pagina in leitor.pages:
                    texto = pagina.extract_text() or ""
                    texto_completo += texto + " "
                    if len(texto_completo.split()) >= self.max_palavras_texto:
                        break
        except Exception:
            logging.exception(f"Falha ao ler PDF: {caminho_pdf}")
        return texto_completo.strip()

    def _extrair_resumo_de_texto(self, texto: str) -> str:
        if not texto:
            return ""
        texto_lower = texto.lower()
        indice_resumo = texto_lower.find('resumo')
        if indice_resumo == -1:
            return ""

        inicio = indice_resumo + len('resumo')
        texto_apos_resumo = texto[inicio:]
        palavras = texto_apos_resumo.split()
        palavras = palavras[:self.max_palavras_resumo]
        return ' '.join(palavras).strip()

    def processar_documentos(self) -> List[Dict[str, str]]:
        resultados = []

        if not os.path.exists(self.pasta_docs):
            logging.error("Pasta de documentos não encontrada: %s", self.pasta_docs)
            return resultados

        for nome in sorted(os.listdir(self.pasta_docs)):
            if not nome.lower().endswith('.pdf'):
                continue

            caminho = os.path.join(self.pasta_docs, nome)
            logging.info("Processando: %s", nome)
            try:
                texto = self._extrair_texto_pdf(caminho)
                resumo = self._extrair_resumo_de_texto(texto)
                if resumo:
                    nome_saida = os.path.splitext(nome)[0] + '_resumo.txt'
                    caminho_saida = os.path.join(self.pasta_resumo, nome_saida)
                    with open(caminho_saida, 'w', encoding='utf-8') as f:
                        f.write(resumo)
                    resultados.append({'nome_arquivo': nome, 'texto': resumo})
                    logging.info("Resumo salvo: %s", nome_saida)
                else:
                    # Fallback: usar as primeiras `fallback_palavras` do texto do documento
                    palavras_doc = texto.split()
                    if palavras_doc:
                        fallback = ' '.join(palavras_doc[:self.fallback_palavras])
                        nome_saida = os.path.splitext(nome)[0] + '_resumo.txt'
                        caminho_saida = os.path.join(self.pasta_resumo, nome_saida)
                        with open(caminho_saida, 'w', encoding='utf-8') as f:
                            f.write(fallback)
                        resultados.append({'nome_arquivo': nome, 'texto': fallback, 'fallback': True})
                        logging.info("Resumo não encontrado; fallback salvo (primeiras %d palavras): %s", self.fallback_palavras, nome_saida)
                    else:
                        logging.info("Resumo e texto não encontrados em: %s", nome)

            except Exception:
                logging.exception("Erro ao processar %s", nome)

        return resultados


def extrair_resumos() -> List[Dict[str, str]]:
    extrator = ExtratorDeResumos()
    return extrator.processar_documentos()


if __name__ == '__main__':
    logging.info("Iniciando extração de resumos...")
    res = extrair_resumos()
    logging.info("Total de resumos extraídos: %d", len(res))