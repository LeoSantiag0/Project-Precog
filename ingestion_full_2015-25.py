import os
import json
import time
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class PrecogScanner:
    def __init__(self):
        self.token = os.getenv("TMDB_READ_TOKEN")
        self.base_url = "https://api.themoviedb.org/3/discover/movie"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "accept": "application/json"
        }

    def capturar_periodo(self, ano_inicio, ano_fim):
        caminho_raw = "data/raw"
        os.makedirs(caminho_raw, exist_ok=True)
        
        for ano in range(ano_inicio, ano_fim + 1):
            print(f"🎬 Iniciando varredura histórica: {ano}")
            filmes_do_ano = []
            pagina = 1
            total_paginas = 1

            while pagina <= total_paginas:
                params = {
                    "language": "pt-BR",
                    "primary_release_year": ano,
                    "sort_by": "vote_count.desc", # Foco nos mais votados primeiro
                    "vote_count.gte": 500,
                    "page": pagina
                }
                
                response = requests.get(self.base_url, headers=self.headers, params=params)
                
                if response.status_code == 200:
                    dados = response.json()
                    if pagina == 1:
                        total_paginas = dados.get('total_pages', 1)
                    
                    filmes_do_ano.extend(dados.get('results', []))
                    print(f"   [Ano {ano}] Página {pagina}/{total_paginas} processada.")
                    
                    pagina += 1
                    time.sleep(0.2) # Respeitando o Rate Limit da API
                else:
                    print(f"   ❌ Falha na comunicação em {ano}, página {pagina}")
                    break
            
            # Persistência por ano (Data Partitioning inicial)
            arquivo_saida = f"{caminho_raw}/movies_{ano}.json"
            with open(arquivo_saida, 'w', encoding='utf-8') as f:
                json.dump(filmes_do_ano, f, ensure_ascii=False, indent=4)
            print(f"✅ Arquivo salvo: {arquivo_saida} ({len(filmes_do_ano)} filmes)")

if __name__ == "__main__":
    scanner = PrecogScanner()
    # Pega de 2015 até o ano atual (2026)
    scanner.capturar_periodo(2015, 2026)