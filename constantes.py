# HTML/CSS para o tema escuro
TEMA_ESCURO_CSS = """<style>
body, .stApp { background-color: #fafafa; color: black; }
.stButton>button { background-color: #eee; color: black; border: 1px solid #aaa; }
</style>
"""

# Se tiver outros trechos, coloque aqui também, por exemplo:
TEMA_CLARO_CSS = """"<style>
body, .stApp { background-color: #111; color: white; }
.stButton>button { background-color: #333; color: white; border: 1px solid #777; }
</style>
"""

CSV_PATH = "data/creditcard.csv"
CSV_PATH_NOT_EXIST = "⚠️ CSV padrão não encontrado. Crie o arquivo em data/padrao.csv."
APIKEY_NOT_EXIST = "⚠️ Defina sua chave GOOGLE_API_KEY no ambiente antes de rodar."
APITOKEN_NOT_EXIST = "⚠️ Defina seu token HF_API_TOKEN no ambiente antes de rodar."
ST_TITLE = "📊 Dashboard AI com CSV-Playground"
PAGE_TITLE = "📊 Dashboard com CSV-Playground"