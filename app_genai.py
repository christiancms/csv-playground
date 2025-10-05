import os
import pandas as pd
import streamlit as st
import plotly.express as px
from io import StringIO, BytesIO
from google import genai
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from google import genai
from dotenv import load_dotenv
import time
from constantes import CSV_PATH_NOT_EXIST, PAGE_TITLE 
from constantes import CSV_PATH, APIKEY_NOT_EXIST, ST_TITLE


class App_Genai:
    # ==========================
    # CONFIGURAÇÕES INICIAIS
    # ==========================
    load_dotenv()
    st.set_page_config(page_title=PAGE_TITLE, layout="wide")
    st.title(ST_TITLE)

    # Inicialize o estado da mensagem se ainda não existir
    if 'show_message' not in st.session_state:
        st.session_state.show_message = False

    # Inicializa cliente Gemini (SDK oficial Google GenAI)
    API_KEY = os.getenv("GOOGLE_API_KEY")
    if not API_KEY:
        st.error(APIKEY_NOT_EXIST)
        st.stop()
    client = genai.Client(api_key=API_KEY)

    # ==========================
    # CSV PADRÃO DO PROJETO
    # ==========================
    # Este é o CSV padrão (por exemplo, na pasta data/)
    

    if not os.path.exists(CSV_PATH):
        st.warning(CSV_PATH_NOT_EXIST)
        st.stop()

    df_default = pd.read_csv(CSV_PATH)
    def exibir_mensagem_temporaria(texto: str, tipo: str = 'info', duracao: int = 3):
        """
        Exibe uma mensagem temporária do Streamlit (st.info, st.success, etc.) 
        por um número específico de segundos e depois a limpa.
        """
        # 1. Cria um placeholder para a mensagem
        placeholder = st.empty()

        # 2. Exibe a mensagem no placeholder com base no tipo
        if tipo == 'info':
            placeholder.info(texto)
        elif tipo == 'success':
            placeholder.success(texto)
        elif tipo == 'warning':
            placeholder.warning(texto)
        elif tipo == 'error':
            placeholder.error(texto)
        else:
            placeholder.info(texto) # Default para info

        # 3. Pausa a execução do Streamlit (CONGELA a interação)
        time.sleep(duracao)

        # 4. Limpa o placeholder, removendo a mensagem
        placeholder.empty()

    # ==========================
    # UPLOAD DE CSV OPCIONAL
    # ==========================
    uploaded_file = st.file_uploader("Carregue outro CSV (opcional)", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        # Chama a função para exibir a mensagem temporária!
        exibir_mensagem_temporaria(
            texto="📁 Usando CSV enviado pelo usuário.", 
            tipo='info', 
            duracao=4 # Exibir por 4 segundos
        )
    else:
        df = df_default
        # Chama a função para exibir a mensagem temporária!
        exibir_mensagem_temporaria(
            texto="📁 Usando CSV padrão do projeto.", 
            tipo='success', 
            duracao=3 # Exibir por 3 segundos
        )

    # ==========================
    # VISUALIZAÇÃO DE DADOS
    # ==========================
    st.subheader("📑 Pré-visualização dos dados")
    st.dataframe(df.head(10), width='stretch')

    # ==========================
    # PERGUNTAS COM GEMINI
    # ==========================
    st.subheader("❓ Faça uma pergunta sobre os dados")

    pergunta = st.text_input("Exemplo: Qual a média da coluna idade?")
    resposta = ""

    if pergunta:
        # Converter DataFrame para CSV em memória (contexto do modelo)
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()

        # Enviar prompt para o Gemini
        with st.spinner("🔍 Analisando com IA..."):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"Você é um analista de dados. Aqui está o CSV:\n\n{csv_data}\n\nPergunta: {pergunta}\nResponda em português de forma clara."
                )
                resposta = response.text.strip()
                st.success(f"🤖 Resposta: {resposta}")
            except Exception as e:
                st.error(f"Erro ao consultar o modelo: {e}")

    # ==========================
    # GRÁFICOS INTERATIVOS
    # ==========================
    st.subheader("📈 Visualização dos Dados")

    colunas_numericas = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    fig = None

    if colunas_numericas:
        coluna = st.selectbox("Escolha uma coluna numérica:", colunas_numericas)
        fig = px.histogram(df, x=coluna, nbins=20, title=f"Distribuição da coluna {coluna}")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhuma coluna numérica disponível para gerar gráficos.")

    # ==============================================
    # GERAR RELATÓRIO EM PDF
    # ==============================================
    st.subheader("🧾 Relatório em PDF")

    def gerar_relatorio(df, pergunta, resposta):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elementos = []

        elementos.append(Paragraph("📊 Relatório de Análise CSV + Gemini", styles["Title"]))
        elementos.append(Spacer(1, 12))

        elementos.append(Paragraph("<b>Resumo dos Dados:</b>", styles["Heading2"]))
        elementos.append(Spacer(1, 8))

        # Tabela com as 5 primeiras linhas
        tabela_dados = [df.columns.tolist()] + df.head(5).values.tolist()
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

        if pergunta:
            elementos.append(Paragraph("<b>Pergunta:</b>", styles["Heading2"]))
            elementos.append(Paragraph(pergunta, styles["Normal"]))
            elementos.append(Spacer(1, 8))
            elementos.append(Paragraph("<b>Resposta da IA:</b>", styles["Heading2"]))
            elementos.append(Paragraph(resposta or "Nenhuma resposta gerada.", styles["Normal"]))
            elementos.append(Spacer(1, 12))

        elementos.append(Paragraph("<i>Relatório gerado automaticamente pelo Dashboard Gemini.</i>", styles["Normal"]))
        doc.build(elementos)
        buffer.seek(0)
        return buffer

    if st.button("🧾 Gerar Relatório em PDF"):
        pdf = gerar_relatorio(df, pergunta, resposta)
        st.download_button(
            label="📥 Baixar Relatório",
            data=pdf,
            file_name="relatorio_gemini.csv.pdf",
            mime="application/pdf",
        )
    
    
