import os
import requests
from dotenv import load_dotenv

# 1. Carrega as variáveis do .env para a memória
load_dotenv()

# 2. Puxa o token da memória
token = os.getenv("TMDB_READ_TOKEN")

# 3. Define a URL de teste (Filmes Populares)
url = "https://api.themoviedb.org/3/movie/popular?language=pt-BR&page=1"

# 4. Configura o cabeçalho de autenticação (Padrão de Mercado)
headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {token}"
}

# 5. Faz a requisição e exibe o resultado
try:
    response = requests.get(url, headers=headers)
    response.raise_for_status() # Levanta um erro se a conexão falhar
    
    dados = response.json()
    print(f"✅ Conexão bem sucedida!")
    print(f"🎬 Primeiro filme da lista: {dados['results'][0]['title']}")

except Exception as e:
    print(f"❌ Erro na conexão: {e}")