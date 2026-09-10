# Relatório 

## 1. Introdução

A taxa de desocupação é um dos principais indicadores da dinâmica econômica e social de uma região. No estado de Pernambuco, o mercado de trabalho enfrentou profundas oscilações na última década, marcadas por momentos de crescimento, períodos de recessão econômica severa e impactos atípicos decorrentes da pandemia de COVID-19. Compreender como essas taxas se comportaram ao longo do tempo e como se distribuem entre diferentes grupos demográficos é fundamental para analisar a realidade do emprego no estado.

### 1.1. Objetivos
O objetivo geral deste trabalho é analisar a evolução da taxa de desocupação em Pernambuco entre 2012 e 2026, utilizando dados abertos da PNAD Contínua (IBGE) tratados com a biblioteca pandas em Python.

Especificamente, busca-se:
- Extrair, higienizar e consolidar os dados trimestrais disponibilizados pela API do IBGE;
- Identificar padrões e ciclos temporais de alta e baixa desocupação no estado;
- Avaliar a existência de desigualdades na taxa de desocupação entre homens e mulheres;
- Mensurar o impacto prático do tratamento de valores omissos sobre os resultados estatísticos.

### 1.2. Perguntas de Pesquisa
A análise é orientada pelas seguintes perguntas norteadoras:
1. **Qual o impacto do tratamento de dados na média calculada?** (Como a remoção de valores nulos/zerados da época da pandemia altera as medidas de tendência central e dispersão?)
2. **Existem diferenças significativas entre os grupos analisados?** (Há disparidade estrutural entre as taxas de desocupação de homens e mulheres ao longo de toda a série temporal?)
3. **Quais foram os principais padrões e ciclos temporais observados no mercado de trabalho pernambucano entre 2012 e 2026?**

## 2. Metodologia e Coleta ETL
Os dados foram coletados diretamente da API de agregados do IBGE (PNAD Contínua), referente à taxa de desocupação trimestral por sexo no estado de Pernambuco, cobrindo o período de 2012 a 2026 ([Link da API](https://servicodados.ibge.gov.br/api/v3/agregados/4093/periodos/201201-202602/variaveis/4099?localidades=N3[26]&classificacao=2[all])).

### 2.1. Extração e Consolidação das Bases
A API retorna os dados em formato JSON com listas aninhadas separando as categorias (Total, Homens e Mulheres). Para consolidar tudo em uma única tabela, percorremos os resultados com um laço `for`, extraímos a série temporal de cada grupo e unificamos tudo em um único DataFrame com o `pd.concat`:

```python
resultados = data['resultados'][0]

dfs = []
for r in resultados:
    nome_categoria = list(r['classificacoes'][0]['categoria'].values())[0].strip().lower()
    serie = r['series'][0]['serie'] 
    s = pd.DataFrame.from_dict(serie, orient='index', columns=[nome_categoria])
    dfs.append(s)

df = pd.concat(dfs, axis=1)
df.index.name = 'periodo'
df = df.reset_index()
```

### 2.2. Limpeza e Tratamento de Dados
Na importação, os valores vieram como texto porque o IBGE usa o caractere `"..."` para indicar períodos sem apuração (como ocorreu em alguns trimestres durante a pandemia de COVID-19). 

Verificamos se havia linhas duplicadas com `df.duplicated().sum()` (resultado 0) e substituímos o `"..."` por `"0"`, convertendo as colunas para o tipo numérico (`float`):

```python
for col in ['total', 'homens', 'mulheres']:
    df[col] = df[col].replace('...', '0').astype(float)

df.info()
```

Saída:
```
 #   Column    Non-Null Count  Dtype  
---  ------    --------------  -----  
 0   periodo   58 non-null     str    
 1   total     58 non-null     float64
 2   homens    58 non-null     float64
 3   mulheres  58 non-null     float64
```

### 2.3. Padronização dos Dados
Para trabalhar com datas de forma adequada, separamos o ano e o trimestre a partir da coluna `periodo` e depois convertemos para o formato de data do pandas (`datetime64`):

```python
df['ano'] = df['periodo'].str[:4]
df['tri'] = df['periodo'].str[-2:].astype(int)

df['periodo'] = pd.PeriodIndex(df['ano'] + 'Q' + df['tri'].astype(str), freq='Q')
df['periodo'] = df['periodo'].dt.to_timestamp()

df.info()
```

Estrutura resultante:
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

### 3.1. Perfil do Dataset
O dataset possui 58 registros trimestrais (de 2012 a 2026). As variáveis são:
- `periodo`: quantitativa contínua / temporal (`datetime64`), marca a data de início do trimestre.
- `total`, `homens`, `mulheres`: quantitativas contínuas (`float64`), representam as taxas de desocupação em %.
- `ano` e `tri`: variáveis qualitativas ordinais / temporais que indicam o ano e o número do trimestre.

### 3.2. Resumo Preliminar e Tratamento de Inconsistências
Aplicando o método `.describe()` na base bruta:

| Métrica | total | homens | mulheres |
| :--- | :---: | :---: | :---: |
| count | 58 | 58 | 58 |
| mean | 10,65% | 9,28% | 12,51% |
| std | 5,30% | 4,88% | 5,96% |
| min | 0,00% | 0,00% | 0,00% |
| 50% (mediana) | 10,90% | 9,50% | 13,05% |
| max | 19,00% | 17,40% | 21,20% |

O valor mínimo de `0,00%` chama a atenção, pois é um resultado artificial vindo dos 8 trimestres com `"..."` da época da pandemia (do 2º trimestre de 2020 ao 1º trimestre de 2022). Para não distorcer as análises, removemos esses períodos sem coleta usando uma consulta simples:

```python
df_filtrado = df.query("total != 0 or mulheres != 0 or homens != 0")
```

Com o filtro, ficamos com 50 registros válidos:

| Métrica | total | homens | mulheres |
| :--- | :---: | :---: | :---: |
| count | 50 | 50 | 50 |
| mean | 12,35% | 10,77% | 14,51% |
| std | 3,34% | 3,37% | 3,43% |
| min | 7,40% | 6,10% | 9,10% |
| 50% (mediana) | 11,80% | 10,15% | 14,30% |
| max | 19,00% | 17,40% | 21,20% |

## 4. Análise Estatística Quantitativa

A análise a seguir utiliza a base filtrada (50 trimestres válidos).

### 4.1. Tendência Central (Média, Mediana e Moda)

Código executado:
```python
print("Média - Total:", df_filtrado['total'].mean())
print("Média - Mulheres:", df_filtrado['mulheres'].mean())
print("Média - Homens:", df_filtrado['homens'].mean())

print("Mediana - Total:", df_filtrado['total'].median())
print("Mediana - Mulheres:", df_filtrado['mulheres'].median())
print("Mediana - Homens:", df_filtrado['homens'].median())

print("Moda - Total:", df_filtrado['total'].mode().values)
print("Moda - Mulheres:", df_filtrado['mulheres'].mode().values)
print("Moda - Homens:", df_filtrado['homens'].mode().values)
```

Resultados:
| Medida | Total | Homens | Mulheres |
| :--- | :---: | :---: | :---: |
| Média | 12,35% | 10,77% | 14,51% |
| Mediana | 11,80% | 10,15% | 14,30% |
| Moda | 9,2% e 14,2% | Multimodal (6,8%, 7,4%...) | Multimodal (10,4%, 11,1%...) |

**Diferenças e implicações práticas:**
- **Sensibilidade da Média a Valores Extremos:** A média aritmética considera o peso de todas as observações, o que a torna altamente sensível a valores extremos. Em todas as colunas, a média é superior à mediana (`12,35% > 11,80%` no Total; `10,77% > 10,15%` em Homens; `14,51% > 14,30%` em Mulheres). Isso ocorre porque os picos atípicos de recessão entre 2016 e 2018 (quando a taxa chegou a 19,0% no Total e 21,2% em Mulheres) puxaram a média para cima, elevando o valor global.
- **Robustez da Mediana:** A mediana divide a base exatamente em 50% dos trimestres acima e 50% abaixo de seu valor. Por ordenar os dados sem ponderar a magnitude dos extremos, ela não é distorcida por crises pontuais, retratando com maior fidelidade o centro típico da taxa de desocupação vivenciada pela população.
- **Comportamento da Moda:** A moda indica o valor mais recorrente. A coluna `total` é bimodal (com modas em 9,2% e 14,2%), o que ilustra com clareza dois regimes econômicos vivenciados em Pernambuco: um primeiro ciclo de relativa estabilidade e baixo desemprego (2012-2014) e um segundo ciclo de crise prolongada (2016-2019).

### 4.2. Variabilidade, Dispersão e Forma da Distribuição

Código executado no pandas para cálculo de variância, desvio padrão, amplitude, assimetria e curtose:
```python
# Variância, Desvio Padrão e Amplitude
for col in ['total', 'mulheres', 'homens']:
    print(f"A variância {col} é:", df_filtrado[col].var())
    print(f"O desvio padrão {col} é:", df_filtrado[col].std())
    print(f"A amplitude {col} é:", df_filtrado[col].max() - df_filtrado[col].min())
    print(f"A assimetria {col} é:", df_filtrado[col].skew())
    print(f"A curtose {col} é:", df_filtrado[col].kurt())
```

Resumo consolidado das métricas:
| Métrica | Total | Homens | Mulheres | Interpretação Resumida |
| :--- | :---: | :---: | :---: | :--- |
| **Variância (`.var()`)** | 11,15 | 11,34 | 11,76 | Dispersão quadrática em torno da média |
| **Desvio Padrão (`.std()`)** | 3,34% | 3,37% | 3,43% | Dispersão média de ~3,4 p.p. em todas as séries |
| **Amplitude (`max - min`)** | 11,60 p.p. (7,4% a 19,0%) | 11,30 p.p. (6,1% a 17,4%) | 12,10 p.p. (9,1% a 21,2%) | Variação ampla entre o melhor e o pior trimestre |
| **Assimetria (`.skew()`)** | +0,28 | +0,47 | +0,07 | Cauda alongada para a direita (picos de crise) |
| **Curtose (`.kurt()`)** | -1,21 | -0,96 | -1,27 | Distribuição platicúrtica (achatada e espalhada) |

**Análise da dispersão e distribuição:**
- **Amplitude e Desvio Padrão:** A amplitude superior a 11 pontos percentuais evidencia a alta oscilação do mercado de trabalho estadual entre fases de crescimento e de recessão. O desvio padrão é muito similar entre homens (3,37%) e mulheres (3,43%), mostrando que os impactos dos ciclos macroeconômicos oscilam com intensidade parecida para ambos, embora as mulheres partam sempre de um patamar médio mais alto.
- **Assimetria e Curtose:** A assimetria positiva (+0,28 no total e +0,47 em homens) reflete a existência de trimestres com picos severos de desocupação (cauda estendida à direita). A curtose negativa em todas as séries caracteriza uma distribuição platicúrtica, ou seja, as taxas se espalham de maneira mais achatada que uma curva normal, sem forte concentração em torno de uma única taxa.

### 4.3. Estratificação dos Dados

#### Comparação por Sexo
Em todos os 50 trimestres analisados, a taxa de desocupação das mulheres foi maior que a dos homens. 
- A diferença média foi de **3,74 pontos percentuais** a mais para as mulheres (14,51% contra 10,77%).
- A menor diferença foi de 1,00 p.p. (no 2º tri de 2018).
- A maior diferença chegou a 6,80 p.p. (no 3º tri de 2022).

#### Comparação Temporal (Médias por Ano)
| Ano | Trimestres | Total | Homens | Mulheres |
| :---: | :---: | :---: | :---: | :---: |
| 2012 | 4 | 9,12% | 7,25% | 11,75% |
| 2013 | 4 | 9,08% | 7,30% | 11,60% |
| 2014 | 4 | 8,25% | 7,18% | 9,78% |
| 2015 | 4 | 9,95% | 8,88% | 11,45% |
| 2016 | 4 | 14,75% | 13,45% | 16,60% |
| 2017 | 4 | 17,85% | 16,45% | 19,75% |
| 2018 | 4 | 16,90% | 15,95% | 18,20% |
| 2019 | 4 | 15,65% | 13,57% | 18,40% |
| 2020 | 1 | 14,80% | 13,40% | 16,70% |
| 2022 | 3 | 13,30% | 10,67% | 16,77% |
| 2023 | 4 | 13,40% | 11,50% | 15,92% |
| 2024 | 4 | 11,22% | 9,32% | 13,68% |
| 2025 | 4 | 10,20% | 8,80% | 12,08% |
| 2026 | 2 | 8,75% | 7,25% | 10,75% |

Pelos dados anuais, nota-se três momentos principais:
1. **2012 a 2014:** Período de desemprego baixo (médias anuais entre 8% e 9%).
2. **2015 a 2019:** Período de crise com forte alta, atingindo o pico em 2017 (média de 17,85% e máxima de 19% no 2º trimestre).
3. **2022 a 2026:** Queda gradual e contínua, voltando para a faixa de 8,75% em 2026.

## 5. Interpretação dos Resultados e Conclusão

### 5.1. Impacto da Limpeza dos Dados
A etapa de tratamento dos nulos foi essencial para não gerar conclusões erradas. Se tivéssemos deixado os valores faltantes como `0`, a média geral de desemprego ficaria em 10,65%. Com a filtragem dos trimestres sem coleta, a média real subiu para 12,35% (uma diferença de 1,70 ponto percentual), e o desvio padrão caiu de 5,30% para 3,34%, eliminando a distorção causada pelos zeros.

### 5.2. Conclusão
A análise dos dados da PNAD Contínua para Pernambuco mostra dois pontos centrais:
- **Sensibilidade econômica:** O mercado de trabalho no estado variou bastante entre 2012 e 2026 (amplitude de 11,6 p.p.), com forte alta nos anos de recessão nacional e recuperação lenta nos anos seguintes, confirmada pela variância e desvio padrão.
- **Desigualdade de gênero:** As mulheres enfrentaram taxas de desocupação mais altas que os homens durante todo o período, com uma diferença média de 3,74 p.p., que aumentou ainda mais nos períodos de recuperação (chegando a 6,8 p.p. em 2022).

O fluxo de extração da API e tratamento com pandas permitiu organizar os dados, corrigir inconsistências e gerar um diagnóstico claro sobre o comportamento do emprego no estado.
