import os
import shutil
import argparse
from pathlib import Path


def listar_conteudo(p: Path):
    items = list(p.iterdir())
    if not items:
        print(f"Pasta vazia: {p}")
        return []
    for it in items:
        print(f" - {it.name} {'(dir)' if it.is_dir() else ''}")
    return items


def apagar_conteudo(p: Path):
    removed_files = 0
    removed_dirs = 0
    for child in p.iterdir():
        try:
            if child.is_dir():
                shutil.rmtree(child)
                removed_dirs += 1
            else:
                child.unlink()
                removed_files += 1
        except Exception as e:
            print(f"Falha ao remover {child}: {e}")
    return removed_files, removed_dirs


def main():
    parser = argparse.ArgumentParser(description="Apaga todo o conteúdo da pasta results (não remove a própria pasta).")
    parser.add_argument("--path", "-p", default=None, help="Caminho para a pasta results. Se omitido, usa ../results relativo ao script.")
    parser.add_argument("--yes", "-y", action="store_true", help="Executa sem pedir confirmação.")
    parser.add_argument("--whatif", action="store_true", help="Lista o que seria removido sem apagar.")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    default_results = (script_dir / '..' / 'results').resolve()
    results_path = Path(args.path).resolve() if args.path else default_results

    if not results_path.exists():
        print(f"Pasta não existe: {results_path}")
        return

    print(f"Local alvo: {results_path}")
    items = listar_conteudo(results_path)
    if not items:
        print("Nada a remover.")
        return

    if args.whatif:
        print("--whatif ativo: nenhuma alteração será feita.")
        return

    if not args.yes:
        resp = input("Confirma remoção de TODOS os arquivos e subpastas acima? [s/N]: ").strip().lower()
        if resp not in ("s", "sim"):
            print("Operação cancelada pelo usuário.")
            return

    files, dirs = apagar_conteudo(results_path)
    print(f"Removidos: {files} arquivos e {dirs} pastas de {results_path}")


if __name__ == '__main__':
    main()
