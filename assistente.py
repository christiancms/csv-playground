import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

class Assistente:

    @staticmethod
    def tipos_de_dados(df):
        return df.dtypes.to_dict()

    @staticmethod
    def intervalo_variaveis(df):
        return df.describe().loc[["min", "max"]].to_dict()

    @staticmethod
    def medidas_tendencia(df):
        return {
            "média": df.mean(numeric_only=True).to_dict(),
            "mediana": df.median(numeric_only=True).to_dict()
        }

    @staticmethod
    def variabilidade(df):
        return {
            "desvio_padrão": df.std(numeric_only=True).to_dict(),
            "variância": df.var(numeric_only=True).to_dict()
        }

    @staticmethod
    def frequencias(df):
        return {col: df[col].value_counts().to_dict() for col in df.columns if df[col].dtype == "object"}

    @staticmethod
    def detectar_outliers(df):
        outliers = {}
        for col in df.select_dtypes(include=["float64", "int64"]).columns:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            filtro = (df[col] < (q1 - 1.5 * iqr)) | (df[col] > (q3 + 1.5 * iqr))
            outliers[col] = df[col][filtro].tolist()
        return outliers

    @staticmethod
    def correlacoes(df):
        return df.corr(numeric_only=True).to_dict()

    @staticmethod
    def agrupamento_kmeans(df, n_clusters=3):
        df_num = df.select_dtypes(include=["float64", "int64"]).dropna()
        scaler = StandardScaler()
        dados_norm = scaler.fit_transform(df_num)
        modelo = KMeans(n_clusters=n_clusters)
        modelo.fit(dados_norm)
        df["cluster"] = modelo.labels_
        return df["cluster"].value_counts().to_dict()

    @staticmethod
    def gerar_grafico(df: pd.DataFrame, coluna: str, tipo: str):
        if coluna not in df.columns:
            return None
        if tipo == "histograma":
            fig = px.histogram(df, x=coluna, nbins=20)
        elif tipo == "boxplot":
            fig = px.box(df, y=coluna)
        elif tipo == "linha":
            fig = px.line(df, y=coluna)
        elif tipo == "pizza":
            contagem = df[coluna].value_counts().reset_index()
            contagem.columns = [coluna, "Contagem"]
            fig = px.pie(contagem, names=coluna, values="Contagem")
        else:
            fig = None
        return fig

    @staticmethod
    def formatar_resposta(resposta_dict, titulo="Resumo"):
        if isinstance(resposta_dict, dict):
            df_formatado = pd.DataFrame(resposta_dict).T.reset_index()
            df_formatado.columns = ["Variável", *df_formatado.columns[1:]]
            return df_formatado
        else:
            return pd.DataFrame([[str(resposta_dict)]], columns=[titulo])

    @staticmethod
    def sugestoes_perguntas(df):
        colunas = df.columns.tolist()
        perguntas = [
            f"Qual a média da coluna {col}?" for col in colunas if df[col].dtype != "object"
        ] + [
            f"Quais os valores mais frequentes na coluna {col}?" for col in colunas if df[col].dtype == "object"
        ]
        return perguntas[:6]
