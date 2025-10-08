### Instalação
Para instalar as dependências localmente (recomendado usar um ambiente virutal `venv`):

```bash
python -m venv .venv
source .venv/bin/activate  # Ativa o venv
pip install -r requirements.txt
```

Streamlit Sharing - consiga rodar o app com 

> pip install -r requirements.txt.

### Interagindo com a IA

#### Descrição dos Dados:
- Quais são os tipos de dados (numéricos, categóricos)?
- Qual a distribuição de cada variável (histogramas, distribuições)?
- Qual o intervalo de cada variável (mínimo, máximo)?
- Quais são as medidas de tendência central (média, mediana)?
- Qual a variabilidade dos dados (desvio padrão, variância)?

#### Identificação de Padrões e Tendências:
- Existem padrões ou tendências temporais?
- Quais os valores mais frequentes ou menos frequentes?
- Existem agrupamentos (clusters) nos dados?

#### Detecção de Anomalias (Outliers):
- Existem valores atípicos nos dados?
- Como esses outliers afetam a análise?
- Podem ser removidos, transformados ou investigados?

#### Relações entre Variáveis:
- Como as variáveis estão relacionadas umas com as outras? (Gráficos de dispersão, tabelas cruzadas)
- Existe correlação entre as variáveis?
- Quais variáveis parecem ter maior ou menor influência sobre outras?


```bash
multi_llm_csv_app/
    ├── app.py                     # Interface principal com Streamlit
    ├── assistant.py               # Funções analíticas e gráficas
    ├── roteador.py                # Roteador inteligente de perguntas
    ├── constantes.py              # Textos e mensagens fixas
    ├── requirements.txt           # Dependências do projeto
    └── data/
        └── exemplo.csv            # CSV padrão para testes

```