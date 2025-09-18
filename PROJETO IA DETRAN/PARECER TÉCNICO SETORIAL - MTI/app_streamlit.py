import streamlit as st
import json
import os
from datetime import datetime
import re

# --- IMPORTAÇÃO DA SUA CLASSE ---
try:
    from gerar_doc import GeradorRelatorioWord
except ImportError:
    st.error("Erro Crítico: O arquivo 'gerar_doc.py' não foi encontrado.")
    st.error("Por favor, verifique se o arquivo da sua classe está na mesma pasta que este script.")
    st.stop()

st.set_page_config(
    page_title="Parecer Técnico Setorial",
    layout="centered",
    page_icon="ico.png",
    initial_sidebar_state="auto"
)

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def validar_numero(numero: str) -> bool:
    # Valida formato "000 / 2025"
    pattern = r"^\d{3} \/ \d{4}$"
    return bool(re.match(pattern, numero))

def validar_data(data: str) -> bool:
    # Valida formato "dd/mm/aaaa"
    try:
        datetime.strptime(data, "%d/%m/%Y")
        return True
    except ValueError:
        return False

st.title("📄 Parecer Técnico Setorial")
st.markdown("Preencha os campos, faça o upload do arquivo JSON e gere seu documento com um clique.")

if st.session_state.get('clear_form', False):
    st.session_state['numero'] = ""
    st.session_state['responsavel'] = ""
    st.session_state['data'] = None
    st.session_state['cargo'] = ""
    st.session_state['numero_processo'] = ""
    st.session_state['constar_psti'] = "Sim"
    st.session_state['iniciativa'] = "Sim"
    st.session_state['acao'] = "Sim"
    st.session_state['tipo_demanda'] = ""
    st.session_state['clear_counter'] = st.session_state.get('clear_counter', 0) + 1
    st.session_state['clear_form'] = False

with st.form(key="report_form"):

    st.header("I - Informações Manuais")

    col1, col2 = st.columns(2)
    with col1:
        numero = st.text_input("Número", placeholder="000/2025", key="numero")
        responsavel = st.text_input("Responsável", key="responsavel")
    with col2:
        data = st.date_input("Data", format="DD/MM/YYYY", key="data")
        cargo = st.text_input("Cargo", key="cargo")
        numero_processo = st.text_input("Número Processo", placeholder="000/2025", key="numero_processo")

    st.header("PSTI")
    constar_psti = st.radio("CONSTA NO PSTI APROVADO", ["Sim", "Não"], horizontal=True, key="constar_psti")
    iniciativa = st.radio("INICIATIVA", ["Sim", "Não"], horizontal=True, key="iniciativa")
    acao = st.radio("AÇÃO", ["Sim", "Não"], horizontal=True, key="acao")

    st.header("DEMANDA")
    tipo_demanda = st.text_input("TIPO DE DEMANDA", placeholder="SETORIAL/CORPORATIVA", key="tipo_demanda")

    st.header("II - Importação e Geração")

    uploaded_file = st.file_uploader(
        "Selecione o arquivo JSON com os itens da demanda",
        type=["json"],
        key=f"uploader_{st.session_state.get('clear_counter', 0)}"
    )

    submit_button = st.form_submit_button(label="✨ Gerar Relatório")

if st.button("🧹 Limpar Formulário"):
    st.session_state['clear_form'] = True
    st.rerun()

if submit_button:
    erros = []
    data_str = data.strftime("%d/%m/%Y") if data else ""
    if not data:
        erros.append("O campo DATA é obrigatório.")

    if erros:
        for erro in erros:
            st.error(erro)
    else:
        if uploaded_file is not None:
            try:
                dados_json = json.load(uploaded_file)
                st.info("✓ JSON carregado.")

                dados_formulario = {
                    "numero": numero,
                    "data": data_str,
                    "responsavel": responsavel,
                    "cargo": cargo,
                    "numero_processo": numero_processo,
                    "ano": numero.split("/")[-1].strip() if "/" in numero else "",
                    "constar_psti": constar_psti,
                    "iniciativa": iniciativa,
                    "acao": acao,
                    "tipo_demanda": tipo_demanda
                }

                dados_finais = {**dados_json, **dados_formulario}
                st.info("✓ Dados mesclados.")

                dados_finais_path = os.path.join(OUTPUT_DIR, 'dados_finais_temp.json')
                with open(dados_finais_path, 'w', encoding='utf-8') as f:
                    json.dump(dados_finais, f, ensure_ascii=False, indent=4)

                st.info("⚙️ Gerando documento... por favor, aguarde.")
                caminho_template = 'templates/template_word.docx'

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                caminho_saida = os.path.join(OUTPUT_DIR, f'relatorio_{timestamp}.docx')

                gerador = GeradorRelatorioWord(caminho_template)
                sucesso = gerador.gerar_documento(
                    caminho_json=dados_finais_path,
                    caminho_saida=caminho_saida
                )

                if sucesso:
                    st.success("🎉 Relatório gerado com sucesso!")

                    with open(caminho_saida, "rb") as file_data:
                        st.download_button(
                            label="Clique aqui para baixar o Relatório (.docx)",
                            data=file_data,
                            file_name=os.path.basename(caminho_saida),
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                else:
                    st.error("✗ Falha ao gerar o documento. A classe de geração indicou um erro. Verifique o console para mais detalhes.")

            except Exception as e:
                st.error(f"Ocorreu um erro inesperado no processo: {e}")
        else:
            st.warning("Por favor, faça o upload de um arquivo JSON para gerar o relatório.")
