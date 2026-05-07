import json
import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

class PrecogEnricherFull:
    def __init__(self):
        self.token = os.getenv("TMDB_READ_TOKEN")
        self.headers = {"Authorization": f"Bearer {self.token}", "accept": "application/json"}
        self.base_url = "https://api.themoviedb.org/3/movie/"

    def executar(self, ano=2026):
        caminho_entrada = f"data/raw/movies_{ano}.json"
        caminho_saida = f"data/raw/movies_details_{ano}.json"
        
        if not os.path.exists(caminho_entrada):
            print(f"❌ Arquivo movies_{ano}.json não encontrado!")
            return

        with open(caminho_entrada, 'r', encoding='utf-8') as f:
            filmes_resumidos = json.load(f)

        detalhes_finais = []
        total = len(filmes_resumidos)
        print(f"🚀 Unindo Discover + Details para o ano {ano}...")

        for i, filme_discover in enumerate(filmes_resumidos, 1):
            movie_id = filme_discover['id']
            url = f"{self.base_url}{movie_id}?language=pt-BR&append_to_response=credits"
            
            try:
                response = requests.get(url, headers=self.headers)
                if response.status_code == 200:
                    details = response.json()
                    
                    # --- FILTRAGEM DOS CRÉDITOS ---
                    crew = details.get('credits', {}).get('crew', [])
                    diretor_obj = next((m for m in crew if m['job'] == 'Director'), None)
                    
                    cast_list = details.get('credits', {}).get('cast', [])[:5]
                    
                    # --- O MERGE COMPLETO ---
                    # Começamos com TODOS os dados que já vieram do Discover
                    filme_completo = filme_discover.copy()
                    
                    # Adicionamos/Sobrescrevemos com os dados novos e limpos do Details
                    filme_completo.update({
                        "budget": details.get("budget"),
                        "revenue": details.get("revenue"),
                        "runtime": details.get("runtime"),
                        "status": details.get("status"),
                        "tagline": details.get("tagline"),
                        "production_companies": [c['name'] for c in details.get("production_companies", [])],
                        "diretor": {
                            "nome": diretor_obj['name'] if diretor_obj else "Desconhecido",
                            "popularidade": diretor_obj['popularity'] if diretor_obj else 0
                        },
                        "elenco_principal": [
                            {"nome": a['name'], "popularidade": a['popularity']} 
                            for a in cast_list
                        ]
                    })
                    
                    detalhes_finais.append(filme_completo)
                    print(f"   [{i}/{total}] ✅ Integrado: {filme_completo['title']}")
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"   ❌ Erro no ID {movie_id}: {e}")

        os.makedirs("data/raw", exist_ok=True)
        with open(caminho_saida, 'w', encoding='utf-8') as f:
            json.dump(detalhes_finais, f, ensure_ascii=False, indent=4)
        
        print(f"\n✨ Arquivo '{caminho_saida}' gerado com sucesso!")

if __name__ == "__main__":
    enricher = PrecogEnricherFull()
    enricher.executar(2026)