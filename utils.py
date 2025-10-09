import chardet

def detectar_encoding(file_obj):
    """
    Detecta o encoding de um arquivo CSV usando chardet.
    Aceita arquivos do tipo BytesIO ou arquivos carregados via Streamlit.
    """
    raw_data = file_obj.read()
    resultado = chardet.detect(raw_data)
    encoding = resultado["encoding"]
    file_obj.seek(0)  # volta ao início para leitura posterior
    
    return encoding

def detectar_separador(file_obj, encoding="utf-8"):
    """
    Detecta automaticamente o separador mais provável entre ',' e ';'
    usando uma amostra do arquivo.
    """
    sample = file_obj.read(2048).decode(encoding)
    file_obj.seek(0)  # volta ao início para leitura posterior

    # Conta quantas colunas seriam geradas com cada separador
    linhas = sample.splitlines()
    if not linhas:
        return ","

    sep_virgula = linhas[0].count(",")
    sep_ponto_e_virgula = linhas[0].count(";")

    return ";" if sep_ponto_e_virgula > sep_virgula else ","

