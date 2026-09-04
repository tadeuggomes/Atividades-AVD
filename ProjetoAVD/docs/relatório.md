# Relatório 

## 1. Introdução:


## 2. Metodologia:
Os dados foram pegos na API do IBGE ([API](https://servicodados.ibge.gov.br/api/v3/agregados/4093/periodos/201201-202602/variaveis/4099?localidades=N3[26]&classificacao=2[all])).

### 2.1. Tratamento de dados gerais:
Inicialmente, os dados foram tratados utilizando o "for", em que listamos as categorias e organizamos as linhas que serão mostradas na tabela de saída, acessando com arrays.

```
resultados = data['resultados'][0]

dfs = []
for r in resultados:
    nome_categoria = list(r['classificacoes'][0]['categoria'].values())[0].strip().lower()  #acessando os dados de acordo com o index.
    serie = r['series'][0]['serie'] 
    s = pd.DataFrame.from_dict(serie, orient='index', columns=[nome_categoria])
    dfs.append(s)

df = pd.concat(dfs, axis=1)
df.index.name = 'periodo'
df = df.reset_index()
```

### 2.2. Tratamento de dados nulos e duplicados:
Para tratar dados nulos e duplicados, fazer uma validação com "..." e "0". O que resulta na substituição dos dados foi feito:

```
for col in ['total', 'homens', 'mulheres']:
    df[col] = df[col].replace('...', '0').astype(float)  # As células da tabela que têm valores duplicados ou nulos, são substituidas por "float64"
df.info()
```

Exemplo de saída para o tratamento de dados duplicados ou nulos:

```
 #   Column    Non-Null Count  Dtype  
---  ------    --------------  -----  
 0   periodo   58 non-null     str    
 1   total     58 non-null     float64
 2   homens    58 non-null     float64
 3   mulheres  58 non-null     float64
```

### 2.3. Padronização dos dados:
No processo de padronização, convertemos variáveis para um tipo adequadro, como a conversão para data:

```
df['ano'] = df['periodo'].str[:4]
df['tri'] = df['periodo'].str[-2:].astype(int)

df['periodo'] = pd.PeriodIndex(df['ano'] + 'Q' + df['tri'].astype(str), freq='Q')

df['periodo'] = df['periodo'].dt.to_timestamp()
```

Exemplo de saída para o processo de padronização de datas:

```
 #   Column    Non-Null Count  Dtype         
---  ------    --------------  -----         
 0   periodo   58 non-null     datetime64[us]
 1   total     58 non-null     float64       
 2   homens    58 non-null     float64       
 3   mulheres  58 non-null     float64       
 4   ano       58 non-null     str           
 5   tri       58 non-null     int64  
```

## 3. Análise Exploratória e Inspeção Inicial

Os dados da API são estruturados em id, sexo e localidade.
- **id**: natureza quantitativa.
- **sexo**: natureza qualitativa.
- **localidade**: natureza qualitativa.

## 4. Análise Estatística Quantitativa

## 5. Interpretação dos Resultados e Conclusão 
