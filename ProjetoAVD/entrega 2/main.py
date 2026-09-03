import requests

url = "https://dados.recife.pe.gov.br/api/action/datastore_search?resource_id=d6f586c3-34c5-4414-9804-6fdfbd75c7db&limit=200000"

r = requests.get(url)
print("Status Code:", r.status_code)

data = r.json()

print(data['result']['records'][0])

registros = data['result']['records']

with open("chamados_samu.json", "w") as f:
    f.write(str(registros))