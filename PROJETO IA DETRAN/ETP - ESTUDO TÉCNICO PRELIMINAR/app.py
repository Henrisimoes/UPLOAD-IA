# app.py

import streamlit as st
from gerar_etp import gerar_etp_completo
from datetime import datetime
import os
from docx import Document
import io
from pathlib import Path

# ========= ESTILO VISUAL =========
st.set_page_config(layout="wide", page_title="Gerador de ETP - DETRAN-MT")

st.markdown("""
    <style>
        .stApp { background-color: #0a2540 !important; }
        [data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"], .main, section.main { background-color: #0a2540 !important; }
        .white-text { color: white !important; }
        div[data-testid="stForm"] { background-color: white; padding: 2rem; border-radius: 15px; }
    </style>
""", unsafe_allow_html=True)

# ========= TÍTULO =========
st.markdown("<h1 class='white-text'>Bem-vindo(a) ao Gerador de Documentos DETRAN-MT</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='white-text'>Insira os dados para a geração do seu ETP (Estudo Técnico Preliminar)</h3>", unsafe_allow_html=True)
st.markdown("---")

# ====================================================================
# --- FUNÇÃO DE EXTRAÇÃO DE DADOS DO DFD (CORREÇÃO DEFINITIVA) ---
# ====================================================================

def extract_data_from_dfd(doc_file_content):
    """
    Extrai dados de MÚLTIPLAS tabelas: uma para dados gerais e outra para a lista de itens.
    """
    try:
        doc = Document(io.BytesIO(doc_file_content))
        items_list = []
        general_data = {}

        # Mapeia os rótulos da tabela do DFD para as chaves do session_state
        # Adicionando variações para garantir a captura
        labels_map = {
            "programa": "programa",
            "projeto/atividade(ação)": "projetoatividade",
            "subação": "subacao",
            "etapa": "etapa",
            "elementodadespesa": "elemento_despesa",
            "fonte": "fonte"
        }

        for table in doc.tables:
            # --- LÓGICA PARA EXTRAIR DADOS GERAIS DA TABELA DE ORÇAMENTO ---
            # Itera nas linhas da tabela, que contêm pares de chave/valor
            for row in table.rows:
                if len(row.cells) >= 2:
                    # Processa o primeiro par de células (ex: Programa | 036)
                    label_1 = row.cells[0].text.replace(":", "").strip()
                    clean_label_1 = "".join(label_1.lower().split())
                    if clean_label_1 in labels_map:
                        key = labels_map[clean_label_1]
                        general_data[key] = row.cells[1].text.strip()

                    # Processa o segundo par de células se a linha tiver 4 células
                    if len(row.cells) >= 4:
                        label_2 = row.cells[2].text.replace(":", "").strip()
                        clean_label_2 = "".join(label_2.lower().split())
                        if clean_label_2 in labels_map:
                            key = labels_map[clean_label_2]
                            general_data[key] = row.cells[3].text.strip()

            # --- LÓGICA PARA EXTRAIR A LISTA DE ITENS DA TABELA DE ITENS ---
            header_row_index = -1
            for i, row in enumerate(table.rows):
                row_text = " ".join([cell.text.strip().upper() for cell in row.cells])
                if "SIAGO/TCE" in row_text and "UN." in row_text and "QTDE" in row_text and "ESPECIFICAÇÃO DO PRODUTO" in row_text:
                    header_row_index = i
                    break
            
            if header_row_index != -1:
                header_row = table.rows[header_row_index]
                header_texts = [cell.text.strip().upper() for cell in header_row.cells]
                
                catmat_idx, desc_idx, un_idx, qtd_idx = -1, -1, -1, -1
                
                for i, text in enumerate(header_texts):
                    if "SIAGO/TCE" in text: catmat_idx = i
                    elif "ESPECIFICAÇÃO" in text or "PRODUTO" in text: desc_idx = i
                    elif "UN." in text: un_idx = i
                    elif "QTDE" in text: qtd_idx = i

                if desc_idx != -1 and un_idx != -1 and qtd_idx != -1:
                    # Limpa a lista de itens para garantir que estamos pegando da tabela correta
                    items_list.clear()
                    for row in table.rows[header_row_index + 1:]:
                        cells = row.cells
                        if len(cells) > max(catmat_idx, desc_idx, un_idx, qtd_idx):
                            item_data = { "catmat": cells[catmat_idx].text.strip() if catmat_idx != -1 else "", "descricao": cells[desc_idx].text.strip(), "unidade": cells[un_idx].text.strip(), "qtd": cells[qtd_idx].text.strip(), "valor_unitario": "" }
                            if item_data["descricao"].strip(): items_list.append(item_data)
        
        return items_list, general_data
    except Exception as e:
        st.error(f"❌ Erro ao ler o documento: '{e}'")
        return None, None

# ====================================================================
# --- ESTADO DA SESSÃO PARA PERSISTÊNCIA DE DADOS ---
# ====================================================================
if 'lista_de_itens_etp' not in st.session_state: st.session_state.lista_de_itens_etp = []

if 'subacao' not in st.session_state: st.session_state.subacao = "xx"
if 'etapa' not in st.session_state: st.session_state.etapa = "xx"
if 'elemento_despesa' not in st.session_state: st.session_state.elemento_despesa = "xxxx-xxxx"
if 'fonte' not in st.session_state: st.session_state.fonte = "xxx"
if 'projetoatividade' not in st.session_state: st.session_state.projetoatividade = ""
if 'programa' not in st.session_state: st.session_state.programa = ""

# ========= INTERFACE DE IMPORTAÇÃO DO DFD ---------
st.markdown("---")
st.markdown("<h3 class='white-text'>Importar Dados do DFD</h3>", unsafe_allow_html=True)
st.markdown("<p class='white-text'>Selecione um DFD (.docx) para importar a lista de itens e os dados de orçamento.</p>", unsafe_allow_html=True)

DFD_FOLDER = Path(r"C:\Users\pedrosilva\Desktop\PROJETO IA DETRAN\DFD - DOCUMENTO DE FORMALIZAÇÃO DE DEMANDA\static\arquivos_gerados")
DFD_FILE_LIST = [f.name for f in DFD_FOLDER.glob("*.docx")] if DFD_FOLDER.exists() else []

if DFD_FILE_LIST:
    selected_file = st.selectbox("Selecione um arquivo DFD:", DFD_FILE_LIST, index=0, key="selected_dfd_file")

    if st.button("✅ Carregar dados do DFD"):
        file_path = DFD_FOLDER / selected_file
        try:
            with open(file_path, "rb") as f:
                imported_items, imported_data = extract_data_from_dfd(f.read())

            if imported_data:
                st.success(f"Dados de orçamento encontrados e carregados!")
                st.session_state.subacao = imported_data.get("subacao", st.session_state.subacao)
                st.session_state.etapa = imported_data.get("etapa", st.session_state.etapa)
                st.session_state.elemento_despesa = imported_data.get("elemento_despesa", st.session_state.elemento_despesa)
                st.session_state.fonte = imported_data.get("fonte", st.session_state.fonte)
                st.session_state.projetoatividade = imported_data.get("projetoatividade", st.session_state.projetoatividade)
                st.session_state.programa = imported_data.get("programa", st.session_state.programa)
            else:
                st.warning("Nenhum dado de orçamento foi encontrado na tabela do documento.")

            if imported_items:
                st.success(f"✅ {len(imported_items)} itens importados com sucesso!")
                st.session_state.lista_de_itens_etp = imported_items
            else:
                st.warning("Nenhuma tabela de itens foi encontrada no documento.")
            
            st.rerun()

        except Exception as e:
            st.error(f"❌ Erro ao processar o arquivo: {e}")
else:
    st.warning("Nenhum arquivo DFD (.docx) encontrado na pasta de origem.")

# ========= FORMULÁRIO PRINCIPAL PARA O ETP =========
with st.form("form_etp"):
    st.subheader("1. Informações Gerais do ETP")
    col1, col2 = st.columns(2)
    with col1:
        etp_numero = st.text_input("Número do ETP", value="003/2025")
        area_requisitante = st.text_input("Área Requisitante", value="COORDENADORIA DE TECNOLOGIA DA INFORMAÇÃO")
    with col2:
        responsavel = st.text_input("Responsável pela Área", value="Danilo Vieira da Cruz")
        
    st.subheader("2. Finalidade Geral e Justificativas")
    finalidade_geral = st.text_area(
        "Finalidade GERAL da Contratação (Base para a IA)",
        value="Aquisição de materiais de consumo (itens de informática) para atender às demandas do Departamento Estadual de Trânsito de Mato Grosso."
    )
    
    st.subheader("3. Detalhes de Planejamento e Orçamento")
    col3, col4, col5, col6 = st.columns(4)
    with col3:
        subacao = st.text_input("Subação", key="subacao")
    with col4:
        etapa = st.text_input("Etapa", key="etapa")
    with col5:
        natureza_despesa = st.text_input("Natureza da Despesa", key="elemento_despesa")
    with col6:
        fonte = st.text_input("Fonte", key="fonte")
    
    col7, col8 = st.columns(2)
    with col7:
        programa = st.text_input("Programa", key="programa")
    with col8:
        projetoatividade = st.text_input("Projeto/Atividade", key="projetoatividade")

    st.subheader("4. Requisitos e Itens da Contratação")
    requisitos_tecnicos = st.text_area("Requisitos Técnicos da Solução")

    st.markdown("---")
    st.markdown("##### Itens da Contratação")
    if st.session_state.lista_de_itens_etp:
        st.dataframe(st.session_state.lista_de_itens_etp, use_container_width=True)
    else:
        st.info("A lista de itens está vazia. Importe de um DFD acima.")

    st.subheader("5. Levantamento de Mercado e Solução")
    solucoes_alternativas = st.text_area("Soluções Alternativas (lista separada por vírgula)")
    solucao_escolhida = st.text_input("Solução Escolhida")

    st.subheader("6. Justificativas e Outras Informações")
    descricao_solucao = st.text_area("Descrição da Solução como um todo")
    justificativa_parcelamento = st.text_area("Justificativa para o parcelamento")
    providencias = st.text_area("Providências a serem adotadas pela Administração")
    correlatas = st.text_area("Contratações correlatas e/ou interdependentes")
    impactos_ambientais = st.text_area("Descrição de possíveis impactos ambientais")
    
    st.subheader("7. Conclusão e Responsabilidade")
    viabilidade = st.radio("Posicionamento Conclusivo", ('É VIÁVEL a presente contratação.', 'NÃO É VIÁVEL a presente contratação.'))
    elaborador_nome = st.text_input("Elaborado por (Nome)", value="XXXXXXXXX")
    elaborador_matricula = st.text_input("Matrícula do Elaborador", value="XXXXXX")
    data_final = st.date_input("Data de Término", value=datetime.now().date())
    
    gerar_etp_button = st.form_submit_button("📥 Gerar ETP Completo", type="primary")

# ====== PROCESSAMENTO E GERAÇÃO DO ETP ========
if gerar_etp_button:
    dados_gerais = {
        'etp_numero': etp_numero, 'area_requisitante': area_requisitante, 'responsavel': responsavel,
        'finalidade_geral': finalidade_geral, 
        'subacao': st.session_state.subacao, 
        'etapa': st.session_state.etapa,
        'elemento_despesa': st.session_state.elemento_despesa, 
        'fonte': st.session_state.fonte, 
        'programa': st.session_state.programa,
        'projetoatividade': st.session_state.projetoatividade, 
        'requisitos_tecnicos': requisitos_tecnicos,
        'solucoes_alternativas': solucoes_alternativas, 'solucao_escolhida': solucao_escolhida,
        'descricao_solucao': descricao_solucao, 'justificativa_parcelamento': justificativa_parcelamento,
        'providencias': providencias, 'correlatas': correlatas, 'impactos_ambientais': impactos_ambientais,
        'viabilidade': viabilidade, 'elaborador_nome': elaborador_nome, 'elaborador_matricula': elaborador_matricula,
        'data_final': data_final.strftime("%d de %B de %Y")
    }

    if not st.session_state.lista_de_itens_etp:
        st.error("❌ Por favor, adicione ao menos um item à tabela do ETP.")
        st.stop()
        
    with st.spinner("Gerando documentos com apoio da IA..."):
        try:
            caminho_docx, dados_json = gerar_etp_completo(dados_gerais, st.session_state.lista_de_itens_etp)

            if caminho_docx and os.path.exists(caminho_docx):
                st.success("✅ Documentos gerados com sucesso!")
                col1, col2 = st.columns(2)
                with col1:
                    with open(caminho_docx, "rb") as f:
                        st.download_button("📥 Baixar ETP (.docx)", f, file_name=os.path.basename(caminho_docx), mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
                with col2:
                    st.download_button("📄 Baixar Dados (.json)", data=dados_json, file_name=os.path.basename(caminho_docx).replace(".docx", "_DATA.json"), mime="application/json", use_container_width=True)
            else:
                st.error("❌ O arquivo não foi gerado ou o caminho retornado é inválido.")
        except Exception as e:
            st.error(f"❌ Erro ao gerar o documento ETP. Detalhes: {e}")
            st.exception(e)