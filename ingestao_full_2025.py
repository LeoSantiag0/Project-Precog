import requests
import json
import os
import time
from dotenv import load_dotenv

# Carrega as chaves do seu arquivo .env
load_dotenv()

class TMDBCollector:
    def __init__(self):
        self.token = os.getenv("TMDB_READ_TOKEN")
        self.base_url = "https://api.themoviedb.org/3/discover/movie"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "accept": "application/json"
        }

    def coletar_ano_inteiro(self, ano):
        todos_os_filmes = []
        pagina_atual = 1
        total_paginas = 1 # Começamos com 1, o código atualizará na primeira chamada

        print(f"🚀 Iniciando extração total de {ano}...")

        while pagina_atual <= total_paginas:
            params = {
                "language": "pt-BR",
                "primary_release_year": ano,
                "sort_by": "vote_average.desc",
                "vote_count.gte": 500,
                "page": pagina_atual
            }

            try:
                response = requests.get(self.base_url, headers=self.headers, params=params)
                response.raise_for_status()
                dados = response.json()

                # Na primeira página, descobrimos quantas existem no total
                if pagina_atual == 1:
                    total_paginas = dados.get('total_pages', 1)
                    print(f"📊 O ano {ano} possui {total_paginas} páginas de dados relevantes.")

                filmes = dados.get('results', [])
                todos_os_filmes.extend(filmes)
                
                print(f"✅ Página {pagina_atual}/{total_paginas} processada. ({len(filmes)} filmes adicionados)")

                # Controle de fluxo: Incrementa a página e pausa para não sobrecarregar a API
                pagina_atual += 1
                time.sleep(0.2) 

            except Exception as e:
                print(f"❌ Falha crítica na página {pagina_atual}: {e}")
                break

        return todos_os_filmes

# --- Bloco de Execução ---
if __name__ == "__main__":
    collector = TMDBCollector()
    
    ano_alvo = 2025
    dados_finais = collector.coletar_ano_inteiro(ano_alvo)

    # Persistência Local (Camada Bronze)
    caminho_pasta = "data/raw"
    os.makedirs(caminho_pasta, exist_ok=True)
    
    arquivo_nome = f"{caminho_pasta}/movies_{ano_alvo}_full.json"
    
    with open(arquivo_nome, 'w', encoding='utf-8') as f:
        json.dump(dados_finais, f, ensure_ascii=False, indent=4)

    print(f"\n✨ Extração Concluída!")
    print(f"📁 Arquivo salvo em: {arquivo_nome}")
    print(f"🎞️ Total de filmes capturados: {len(dados_finais)}")