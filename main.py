import os
import sys
# Adiciona o diretório raiz do projeto ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src import starter, originals, duplicate, scrap, filter, name, save  # Importa os módulos da pasta src

# Configurações iniciais
MODULES = [starter, originals, duplicate, scrap, filter, name, save]  # Lista de módulos importados

def run_module(module):
    """
    Executa um módulo específico.
    """
    try:
        print(f"Executando {module.__name__}...")
        module.main()  # Chama a função main() do módulo
        print(f"{module.__name__} executado com sucesso.\n")
    except Exception as e:
        print(f"Erro ao executar {module.__name__}:")
        print(e)  # Imprime o erro retornado pelo módulo
        raise

def main():
    """
    Executa todos os módulos em sequência.
    """
    for module in MODULES:
        run_module(module)

if __name__ == "__main__":
    main()