import os
import json
import time
import requests
from tqdm import tqdm
from dotenv import load_dotenv

# Carregar credenciais do arquivo .env
load_dotenv()

class TMDBRawIngestor:
    def __init__(self):
        self.token = os.getenv("TMDB_READ_TOKEN")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "accept": "application/json"
        }
        self.discover_url = "https://api.themoviedb.org/3/discover/movie"
        self.details_url = "https://api.themoviedb.org/3/movie/"

    def _get_movie_enrichment(self, movie_id):
        """
        Privado: Procura detalhes e créditos filtrados numa única chamada.
        Retorna apenas os campos necessários para o modelo de ML.
        """
        url = f"{self.details_url}{movie_id}?language=pt-BR&append_to_response=credits"
        try:
            res = requests.get(url, headers=self.headers)
            if res.status_code == 200:
                data = res.json()
                
                # Extração cirúrgica do Diretor
                crew = data.get('credits', {}).get('crew', [])
                director = next((m for m in crew if m['job'] == 'Director'), None)
                
                # Extração cirúrgica do Elenco (Top 5)
                cast = data.get('credits', {}).get('cast', [])[:5]

                return {
                    "budget": data.get("budget"),
                    "revenue": data.get("revenue"),
                    "runtime": data.get("runtime"),
                    "production_companies": [c['name'] for c in data.get("production_companies", [])],
                    "status": data.get("status"),
                    "director_data": {
                        "name": director['name'] if director else "Unknown",
                        "popularity": director['popularity'] if director else 0
                    },
                    "top_cast_data": [
                        {"name": a['name'], "popularity": a['popularity']} 
                        for a in cast
                    ]
                }
        except Exception:
            return {}
        return {}

    def run_historical_ingestion(self, start_year=2015, end_year=2026):
        """
        Executa a carga completa do período definido.
        Organiza os ficheiros na subpasta data/raw/tmdb/.
        """
        # Define o caminho soberano da fonte
        raw_path = os.path.join("data", "raw", "tmdb")
        os.makedirs(raw_path, exist_ok=True)
        
        print(f"🚀 Iniciando Pipeline de Ingestão Raw: {start_year} - {end_year}")

        for year in range(start_year, end_year + 1):
            movies_accumulator = []
            
            # Parametrizar a busca inicial no Discover
            params = {
                "language": "pt-BR",
                "primary_release_year": year,
                "sort_by": "vote_count.desc",
                "vote_count.gte": 500,
                "page": 1
            }
            
            try:
                initial_res = requests.get(self.discover_url, headers=self.headers, params=params)
                if initial_res.status_code != 200:
                    print(f"⚠️ Erro ao aceder ao ano {year}. Status: {initial_res.status_code}")
                    continue
                    
                data_iniciais = initial_res.json()
                total_pages = data_iniciais.get('total_pages', 1)
                total_results = data_iniciais.get('total_results', 0)

                # Barra de progresso visual para o ano corrente
                pbar = tqdm(total=total_results, desc=f"📅 {year}", unit="movie", bar_format='{l_bar}{bar:30}{r_bar}')

                for page in range(1, total_pages + 1):
                    params["page"] = page
                    page_res = requests.get(self.discover_url, headers=self.headers, params=params)
                    
                    if page_res.status_code == 200:
                        for movie in page_res.json().get('results', []):
                            # Faz o Merge: Dados do Discover + Enriquecimento do Details
                            enrichment = self._get_movie_enrichment(movie['id'])
                            movie.update(enrichment)
                            
                            movies_accumulator.append(movie)
                            pbar.update(1)
                            time.sleep(0.05) # Proteção de Rate Limit
                    else:
                        break
                
                pbar.close()

                # Guarda o ficheiro particionado na subpasta da fonte
                output_file = os.path.join(raw_path, f"movies_details_{year}.json")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(movies_accumulator, f, ensure_ascii=False, indent=4)
            
            except Exception as e:
                print(f"\n❌ Falha no processamento do ano {year}: {e}")
        
        print(f"\n✅ Ingestão Concluída. Camada RAW TMDB populada em: {raw_path}")

if __name__ == '__main__':
    ingestor = TMDBRawIngestor()
    ingestor.run_historical_ingestion()