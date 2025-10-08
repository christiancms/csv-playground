from assistente import Assistente


def roteador_de_pergunta(pergunta: str, df):
    pergunta_lower = pergunta.lower()
    resposta = None
    tipo = "modelo"

    if "tipo de dado" in pergunta_lower or "tipos de dados" in pergunta_lower:
        resposta = Assistente.tipos_de_dados(df)
        tipo = "assistente"
    elif any(p in pergunta_lower for p in ["intervalo", "mínimo", "minimo", "min", "max", "maximo", "máximo"]):
        resposta = Assistente.intervalo_variaveis(df)
        tipo = "assistente"
    elif "média" in pergunta_lower or "mediana" in pergunta_lower:
        resposta = Assistente.medidas_tendencia(df)
        tipo = "assistente"
    elif any(p in pergunta_lower for p in ["desvio padrão", "desvio padrao", "variancia", "variância"]):
        resposta = Assistente.variabilidade(df)
        tipo = "assistente"
    elif "frequente" in pergunta_lower or "menos frequente" in pergunta_lower:
        resposta = Assistente.frequencias(df)
        tipo = "assistente"
    elif any(p in pergunta_lower for p in ["outlier", "atipico", "valor atípico"]):
        resposta = Assistente.detectar_outliers(df)
        tipo = "assistente"
    elif any(p in pergunta_lower for p in ["correlação","correlacao", "relacionadas"]):
        resposta = Assistente.correlacoes(df)
        tipo = "assistente"
    elif "cluster" in pergunta_lower or "agrupamento" in pergunta_lower:
        resposta = Assistente.agrupamento_kmeans(df)
        tipo = "assistente"
    return resposta, tipo
