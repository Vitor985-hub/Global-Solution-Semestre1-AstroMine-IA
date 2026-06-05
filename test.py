import requests

API_KEY = "pdkPCd484vP7TNeKThte7SjmJar7IylOY1numgyb"  # Substitua pela sua chave oficial da NASA
START_DATE = "2026-06-01"
END_DATE = "2026-06-03" # Limite máximo de intervalo de 7 dias na NeoWs

url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={START_DATE}&end_date={END_DATE}&api_key={API_KEY}"


resonse = requests.get(url)

print(resonse.json())