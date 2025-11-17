import os
import re
import unicodedata
import json
from typing import List
from collections import Counter

#----------------------------------------------------------------------------------------#
def remover_acentos(texto: str) -> str:
	nfkd = unicodedata.normalize('NFD', texto)
	return ''.join([c for c in nfkd if not unicodedata.combining(c)])

#----------------------------------------------------------------------------------------#
def carregar_stopwords(caminho_stopwords: str) -> set:
	palavras = set()
	if not os.path.exists(caminho_stopwords):
		raise FileNotFoundError(f"Arquivo de stopwords não encontrado: {caminho_stopwords}")
	
	# tenta utf-8 primeiro, senão latin-1
	try:
		with open(caminho_stopwords, 'r', encoding='utf-8') as f:
			linhas = f.readlines()
	except UnicodeDecodeError:
		with open(caminho_stopwords, 'r', encoding='latin-1') as f:
			linhas = f.readlines()

	for linha in linhas:
		w = linha.strip()
		if not w:
			continue
		w = remover_acentos(w).lower()
		palavras.add(w)
	return palavras

#----------------------------------------------------------------------------------------#
def normalizar_token(token: str) -> str:
	# Remove acentos
	t = remover_acentos(token)
	# Mantém hífens que aparecem entre duas letras (ex: "micro-ambiente")
	chars = []
	for i, c in enumerate(t):
		if c.isalpha():
			chars.append(c)
		elif c == '-' and i > 0 and i < len(t) - 1 and t[i-1].isalpha() and t[i+1].isalpha():
			chars.append(c)
		else:
			# ignora outros caracteres
			continue
	t = ''.join(chars).lower()
	
	# Normalização simples para plural: remove 's' e 'es' no final
	if t.endswith('es') and len(t) > 3:
		t = t[:-2]
	elif t.endswith('s') and len(t) > 2:
		t = t[:-1]
	return t
	

#----------------------------------------------------------------------------------------#
def normalizar_arquivo(caminho_entrada: str, caminho_saida: str, stopwords: set) -> Counter:
	with open(caminho_entrada, 'r', encoding='utf-8') as f:
		texto = f.read()

	# Substitui quebras de linha e hífens que separam palavras ao fim da linha
	texto = texto.replace('-\n', '')
	texto = texto.replace('\n', ' ')

	# Tokeniza por espaços
	raw_tokens = re.split(r"\s+", texto)

	tokens_norm = []
	for tok in raw_tokens:
		if not tok:
			continue
		t = normalizar_token(tok)
		if not t or len(t) < 2:
			continue
		if t in stopwords:
			continue
		tokens_norm.append(t)

	# Escreve arquivo de saída
	with open(caminho_saida, 'w', encoding='utf-8') as f:
		f.write(' '.join(tokens_norm))

	return Counter(tokens_norm)

#----------------------------------------------------------------------------------------#
def processar_pasta_results(apenas_novos: List[str] = None):
	src_dir = os.path.dirname(__file__)
	raiz = os.path.abspath(os.path.join(src_dir, '..'))
	pasta_results = os.path.join(raiz, 'results')
	pasta_resumos = os.path.join(pasta_results, 'resumo')
	pasta_normalizado = os.path.join(pasta_results, 'normalizado')
	caminho_stop = os.path.join(raiz, 'stopwords.txt')

	stopwords = carregar_stopwords(caminho_stop)
	os.makedirs(pasta_normalizado, exist_ok=True)

	# Carrega o JSON existente se estivermos atualizando
	freq_json_path = os.path.join(pasta_results, 'frequencies_summary.json')
	dados_simples = {}
	if apenas_novos and os.path.exists(freq_json_path):
		try:
			with open(freq_json_path, 'r', encoding='utf-8') as jf:
				dados_simples = json.load(jf)
		except (json.JSONDecodeError, FileNotFoundError):
			print("Arquivo frequencies_summary.json não encontrado ou corrompido. Criando um novo.")
			dados_simples = {}

	arquivos_a_processar = apenas_novos if apenas_novos else os.listdir(pasta_resumos)

	for nome in arquivos_a_processar:
		if not nome.lower().endswith('.txt'):
			continue

		# Constrói o nome do arquivo de saída como "Arquivo_termos.txt"
		if nome.lower().endswith('_resumo.txt'):
			base_nome = nome[:-len('_resumo.txt')]
		else:
			base_nome = os.path.splitext(nome)[0]
		saida_nome = f"{base_nome}_termos.txt"

		caminho = os.path.join(pasta_resumos, nome)
		caminho_saida = os.path.join(pasta_normalizado, saida_nome)

		try:
			freqs = normalizar_arquivo(caminho, caminho_saida, stopwords) # freqs é um Counter
			
			pdf_nome = f"{base_nome}.pdf"
			freq_list = [[t, c] for t, c in freqs.most_common()]
			dados_simples[pdf_nome] = freq_list

			print(f"Arquivo normalizado e adicionado ao índice: {nome} (termos únicos: {len(freqs)})")
		except Exception as e:
			print(f"Erro ao normalizar {nome}: {e}")

	# Escreve o JSON simples
	with open(freq_json_path, 'w', encoding='utf-8') as jf:
		json.dump(dados_simples, jf, ensure_ascii=False, indent=2)

	print(f'Normalização concluída.\n\nSalvo em: {freq_json_path}')

#----------------------------------------------------------------------------------------#
if __name__ == '__main__':
	processar_pasta_results()