import requests

url =  "https://servicodados.ibge.gov.br/api/v3/agregados/4093/periodos/201201|201202-202601/variaveis/4093|4096|4099|12466?localidades=N3[26]&classificacao=2[all]"


r = requests.get(url)
print ("Status Code:", r.status_code)


data = r.json()

print (data[0]['resultados'][1]['series'][0]['serie'])


valores0 = data[0]['resultados'][0]['series'][0]['serie']

with open("TOTAL4093.json", "w") as f:
    f.write(str(valores0))

valores1 = data[0]['resultados'][1]['series'][0]['serie']

with open("homens4093.json", "w") as f:
    f.write(str(valores1))

valores2 = data[0]['resultados'][2]['series'][0]['serie']

with open("mulheres4093.json", "w") as f:
    f.write(str(valores2))

valores3 = data[1]['resultados'][0]['series'][0]['serie']
with open("TOTAL4096.json", "w") as f:
    f.write(str(valores3))

valores4 = data[1]['resultados'][1]['series'][0]['serie']
with open("homens4096.json", "w") as f:
    f.write(str(valores4))

valores5 = data[1]['resultados'][2]['series'][0]['serie']
with open("mulheres4096.json", "w") as f:
    f.write(str(valores5))

valores6 = data[2]['resultados'][0]['series'][0]['serie']
with open("TOTAL4099.json", "w") as f:
    f.write(str(valores6))

valores7 = data[2]['resultados'][1]['series'][0]['serie']
with open("homens4099.json", "w") as f:
    f.write(str(valores7))

valores8 = data[2]['resultados'][2]['series'][0]['serie']
with open("mulheres4099.json", "w") as f:
    f.write(str(valores8))

valores9 = data[3]['resultados'][0]['series'][0]['serie']
with open("TOTAL12466.json", "w") as f:
    f.write(str(valores9))

valores10 = data[3]['resultados'][1]['series'][0]['serie']
with open("homens12466.json", "w") as f:
    f.write(str(valores10))
valores11 = data[3]['resultados'][2]['series'][0]['serie']
with open("mulheres12466.json", "w") as f:
    f.write(str(valores11))
