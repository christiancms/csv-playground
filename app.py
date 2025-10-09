import os
import requests
import pandas as pd
import streamlit as st
import plotly.express as px
from io import StringIO, BytesIO
from reportlab.lib.pagesizes import A4, A2, A0, landscape, portrait
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
import google.generativeai as genai
from dotenv import load_dotenv
from assistente import Assistente
from roteador import roteador_de_pergunta
import time
import json
from langdetect import detect
from constantes import CSV_PATH_NOT_EXIST, PAGE_TITLE
from constantes import CSV_PATH, APIKEY_NOT_EXIST, ST_TITLE, APITOKEN_NOT_EXIST


class App:
    # ==========================
    # CONFIGURAÇÕES INICIAIS
    # ==========================
    def __init__(self):
        load_dotenv()
        st.set_page_config(page_title=PAGE_TITLE, layout="wide")
        st.title(ST_TITLE)
        self.api_key = os.getenv("GOOGLE_API_KEY")
        # Inicializa cliente Gemini (SDK oficial Google GenAI)
        if not self.api_key:
            st.error(APIKEY_NOT_EXIST)
            st.stop()
        genai.configure(api_key=self.api_key)
        # Crie o modelo
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        self.df = self.carregar_csv()
        self.historico = st.session_state.get("historico", {})

        self.api_token = os.getenv("HF_API_TOEKN")
        if not self.api_token:
            st.error(APITOKEN_NOT_EXIST)
            st.stop()
        self.headers = {"Authorization": f"Bearer {self.api_token}"}
    

    def hf_infer(self, prompt, model="mistralai/Mistral-7B-Instruct-v0.2"):
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{model}",
            headers=self.headers,
            json={"inputs": prompt}
        )
        return response.json()[0]["generated_text"]

    # ==========================
    # CSV PADRÃO DO PROJETO
    # ==========================
    # Este é o CSV padrão (por exemplo, na pasta data/)
    def carregar_csv(self):
        uploaded_file = st.file_uploader("📁 Carregue um CSV (opcional)", type=["csv"])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            self.exibir_mensagem("📁 Usando CSV enviado pelo usuário.", "info")
        else:
            if not os.path.exists(CSV_PATH):
                st.warning(CSV_PATH_NOT_EXIST)
                st.stop()
            df = pd.read_csv(CSV_PATH)
            self.exibir_mensagem("📁 Usando CSV padrão do projeto.", "success")
        return df

    def exibir_mensagem(self, texto, tipo="info", duracao=3):
        placeholder = st.empty()
        getattr(placeholder, tipo)(texto)
        time.sleep(duracao)
        placeholder.empty()

    def detectar_idioma(self, texto):
        try:
            return detect(texto)
        except:
            return "pt"

    def gerar_prompt(self, pergunta, csv_data, idioma):
        if idioma == "en":
            return f"You are a data analyst. Here's the CSV:\n\n{csv_data}\n\nQuestion: {pergunta}\nRespond clearly in English."
        elif idioma == "es":
            return f"Eres un analista de datos. Aquí está el CSV:\n\n{csv_data}\n\nPregunta: {pergunta}\nResponde claramente en español."
        else:
            return f"Você é um analista de dados. Aqui está o CSV:\n\n{csv_data}\n\nPergunta: {pergunta}\nResponda em português de forma clara."

    def responder_pergunta(self):
        st.subheader("❓ Faça uma pergunta sobre os dados")
        for p in Assistente.sugestoes_perguntas(self.df):
            st.markdown(f"- {p}")
        pergunta = st.text_input("Digite sua pergunta")
        if not pergunta:
            return
        if pergunta.lower() in self.historico:
            st.success("🔁 Resposta recuperada do histórico:")
            st.dataframe(self.historico[pergunta.lower()])
            return
        with st.spinner("🔍 Analisando..."):
            resposta, tipo = roteador_de_pergunta(pergunta, self.df)
            if tipo == "assistente":
                resposta_formatada = Assistente.formatar_resposta(resposta)
                st.success("📊 Resposta gerada pelo assistente:")
                st.dataframe(resposta_formatada)
                fig = Assistente.gerar_grafico(resposta_formatada, "Variável", resposta_formatada.columns[1])
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                self.historico[pergunta.lower()] = resposta_formatada
            else:
                csv_buffer = StringIO()
                self.df.to_csv(csv_buffer, index=False)
                prompt = self.gerar_prompt(pergunta, csv_buffer.getvalue(), self.detectar_idioma(pergunta))
                try:
                    response = self.responder_com_llm(prompt)
                    resposta_texto = response
                    st.success(f"🤖 Resposta da IA: {resposta_texto}")
                    self.historico[pergunta.lower()] = pd.DataFrame([[resposta_texto]], columns=["Resposta"])
                except Exception as e:
                    st.error(f"Erro ao consultar o modelo: {e}")

    def gerar_grafico_manual(self):
        st.subheader("📊 Gerar gráfico sob demanda")
        tipo = st.selectbox("Tipo de gráfico", ["histograma", "boxplot", "linha", "pizza"])
        colunas = self.df.select_dtypes(include=["float64", "int64"]).columns if tipo != "pizza" else self.df.select_dtypes(include=["object"]).columns
        coluna = st.selectbox("Escolha a coluna", colunas)
        if st.button("📈 Gerar gráfico"):
            fig = Assistente.gerar_grafico(self.df, coluna, tipo)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Não foi possível gerar o gráfico.")

    def exportar_resultados(self):
        st.subheader("📥 Exportar Resultados")
        if st.button("📥 Baixar histórico de perguntas"):
            historico_json = json.dumps({k: v.to_dict() if isinstance(v, pd.DataFrame) else str(v) for k, v in self.historico.items()}, indent=2, ensure_ascii=False)
            st.download_button("📥 Download JSON", data=historico_json, file_name="historico_perguntas.json", mime="application/json")
        if st.button("📥 Baixar última resposta como CSV"):
            ultima = list(self.historico.values())[-1] if self.historico else None
            if isinstance(ultima, pd.DataFrame):
                buffer = StringIO()
                ultima.to_csv(buffer, index=False)
                st.download_button("📥 Download CSV", data=buffer.getvalue(), file_name="resposta.csv", mime="text/csv")


    # FALLBACK
    def responder_com_llm(self, prompt):
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except:
            return self.hf_infer(prompt)  # usa Hugging Face se Gemini falhar
        
    # ==============================================
    # GERAR RELATÓRIO EM PDF
    # ==============================================
    def gerar_pdf(self):
        st.subheader("🧾 Gerar Relatório em PDF")
        pergunta = st.text_input("Pergunta para incluir no relatório")
        resposta = self.historico.get(pergunta.lower())
        orientacao = st.radio("Orientação do PDF", ["paisagem", "retrato"], index=0)

        if st.button("🧾 Gerar PDF"):
            buffer = BytesIO()
            # Escolher orientação
            tamanho_pagina = landscape(A0) if orientacao == "paisagem" else portrait(A4)

            # Criar documento com margens de 1cm
            doc = SimpleDocTemplate(
                buffer,
                pagesize=tamanho_pagina,
                leftMargin=1 * cm,
                rightMargin=1 * cm,
                topMargin=1 * cm,
                bottomMargin=1 * cm,
            )

            styles = getSampleStyleSheet()
            elementos = [Paragraph("📊 Relatório de Análise CSV + IA", styles["Title"]), Spacer(1, 12)]

            elementos.append(Paragraph("<b>Resumo dos Dados:</b>", styles["Heading2"]))
            elementos.append(Spacer(1, 8))
            
            # Tabela com as 5 primeiras linhas
            tabela_dados = [self.df.columns.tolist()] + self.df.head(5).values.tolist()
            tabela = Table(tabela_dados)
            tabela.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ]))
            elementos.append(tabela)
            elementos.append(Spacer(1, 12))
            elementos.append(Paragraph("<b>Pergunta:</b>", styles["Heading2"]))
            elementos.append(Paragraph(pergunta, styles["Normal"]))
            elementos.append(Spacer(1, 8))
            elementos.append(Paragraph("<b>Resposta:</b>", styles["Heading2"]))
            elementos.append(Paragraph(str(resposta) if resposta is not None else "Nenhuma resposta encontrada.", styles["Normal"]))
            doc.build(elementos)
            buffer.seek(0)
            st.download_button("📥 Baixar Relatório", data=buffer, file_name="relatorio.pdf", mime="application/pdf")

    def executar(self):
        st.subheader("📑 Pré-visualização dos dados")
        st.dataframe(self.df.head(10), width="stretch")
        self.responder_pergunta()
        self.gerar_grafico_manual()
        self.exportar_resultados()
        self.gerar_pdf()
        st.session_state.historico = self.historico


# Executa o app
if __name__ == "__main__":
    App().executar()
