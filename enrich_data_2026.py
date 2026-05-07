import json
import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

class PrecogEnricher:
    def __init__(self):
        self.token = os.getenv("TMDB_READ_TOKEN")
        self.headers = {"Authorization": f"Bearer {self.token}", "accept": "application/json"}
        self.base_url = "https://api.themoviedb.org/3/movie/"

    def enriquecer_2026(self):
        caminho_entrada = "data/raw/movies_2026.json"
        caminho_saida = "data/raw/movies_details_2026.json"
        
        if not os.path.exists(caminho_entrada):
            print("❌ Erro: O arquivo movies_2026.json não foi encontrado em data/raw/")
            return

        with open(caminho_entrada, 'r', encoding='utf-8') as f:
            filmes_resumidos = json.load(f)

        detalhes_completos = []
        total = len(filmes_resumidos)
        print(f"🧬 Iniciando enriquecimento de {total} filmes de 2026...")

        for i, filme in enumerate(filmes_resumidos, 1):
            movie_id = filme['id']
            titulo = filme.get('title', 'Sem título')
            
            try:
                # Chamada ao endpoint de detalhes
                response = requests.get(f"{self.base_url}{movie_id}?language=pt-BR", headers=self.headers)
                
                if response.status_code == 200:
                    detalhe = response.json()
                    
                    # Unindo o que já tínhamos (filme) com os novos detalhes (detalhe)
                    # O operador ** faz o merge dos dicionários
                    filme_completo = {**filme, **detalhe}
                    detalhes_completos.append(filme_completo)
                    print(f"   [{i}/{total}] ✅ Detalhes obtidos: {titulo}")
                else:
                    print(f"   [{i}/{total}] ⚠️ Falha ao buscar: {titulo} (Status: {response.status_code})")
                
            except Exception as e:
                print(f"   [{i}/{total}] ❌ Erro inesperado em {titulo}: {e}")
            
            # Pequena pausa para respeitar a API
            time.sleep(0.1)

        # Salvando o resultado final
        os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
        with open(caminho_saida, 'w', encoding='utf-8') as f:
            json.dump(detalhes_completos, f, ensure_ascii=False, indent=4)
        
        print(f"\n✨ Sucesso! O arquivo enriquecido foi salvo em: {caminho_saida}")

if __name__ == "__main__":
    enricher = PrecogEnricher()
    enricher.enriquecer_2026()