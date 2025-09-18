import json
import locale as lc
from datetime import datetime
from pathlib import Path
import uuid
from pprint import pprint

import jinja2
from docxtpl import DocxTemplate
import streamlit as st
from PIL import Image
import pandas as pd

from padroes import TD, CustomEncoder, Itens, int_para_string, dinheiro_para_string, format_by, fmt_real
from utils import LogLevel, log

lc.setlocale(lc.LC_ALL, "C")  # Reset para um locale padrão antes de tentar pt_BR

try:
    lc.setlocale(lc.LC_TIME, "pt_BR.UTF-8")
    lc.setlocale(lc.LC_CTYPE, "pt_BR.UTF-8")
    lc.setlocale(lc.LC_MONETARY, "pt_BR.UTF-8")
except lc.Error:
    try:
        lc.setlocale(lc.LC_TIME, "pt_BR")
        lc.setlocale(lc.LC_CTYPE, "pt_BR")
        lc.setlocale(lc.LC_MONETARY, "pt_BR")
    except lc.Error:
        lc.setlocale(lc.LC_TIME, "")  # Fallback para o padrão do sistema
        lc.setlocale(lc.LC_CTYPE, "")
        lc.setlocale(lc.LC_MONETARY, "")

cwd = Path(__file__).resolve().parent


def group_str(text: str, by: int):
    rev = text[::-1]
    t = [rev[i : i + by] for i in range(0, len(rev), by)]
    return ".".join([x[::-1] for x in t[::-1]])


# ========== TÍTULO COM LOGO ==========
logo_path = cwd.parent / "DFD - DOCUMENTO DE FORMALIZAÇÃO DE DEMANDA" / "static" / "logo_detran.png"

st.write(f"Streamlit Version: {st.__version__}")

st.set_page_config(layout="wide")

st.markdown('<div class="title-container">', unsafe_allow_html=True)

if logo_path.exists():
    logo = Image.open(logo_path)
    st.image(logo, width=60)
else:
    st.warning(f"Logo não encontrada em: {logo_path}. Verifique o caminho.")

st.markdown('<div class="title-text">Gerador de Instrumento Simplificado De Formalização De Demanda - DETRAN-MT</div>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

if "numero_isfd" not in st.session_state:
    st.session_state.numero_isfd = 1
if "ano_isfd" not in st.session_state:
    st.session_state.ano_isfd = datetime.now().year
if "unit_orc" not in st.session_state:
    st.session_state.unit_orc = None
if "tipo_despesa" not in st.session_state:
    st.session_state.tipo_despesa = None
if "content_empty" not in st.session_state:
    st.session_state.content_empty = True

if "dfd_key" not in st.session_state:
    st.session_state.dfd_key = uuid.uuid4()
if "etp_key" not in st.session_state:
    st.session_state.etp_key = uuid.uuid4()
if "lista_itens" not in st.session_state:
    st.session_state.lista_itens = []

input_path = cwd / "template" / "Template-ISFD.docx"
output_path = cwd / "output"

output_path.mkdir(parents=True, exist_ok=True)

if not input_path.exists():
    raise FileNotFoundError(f'Arquivo de template nao encontrado em "{input_path}"')

jinja_env = jinja2.Environment()
jinja_env.globals["TD"] = TD
jinja_env.globals["int_para_string"] = int_para_string
jinja_env.globals["fmt_real"] = fmt_real
jinja_env.filters["format_by"] = format_by

tpl = DocxTemplate(input_path)

context: dict = dict.fromkeys(tpl.get_undeclared_template_variables(jinja_env))


tipos_despesa = [
    "Capacitaçao",
    "Equipamento de Apoio e demais investimentos",
    "Equipamento de TI",
    "Consultoria / Auditoria / Assessoria",
    "Despesas de Custeio",
    "Bens de Consumo",
    "Obras / Reformas / Serviços de Engenharia",
]

docx_path: Path = None

with st.container(border=True):
    st.subheader("Carregar Dados do DFD/ETP (Opcional)", anchor=False)

    # DFD - DOCUMENTO DE FORMALIZAÇÃO DE DEMANDA\static\arquivos_gerados
    dfd_path = cwd.parent / "DFD - DOCUMENTO DE FORMALIZAÇÃO DE DEMANDA" / "static" / "arquivos_gerados"
    dfd_path.mkdir(parents=True, exist_ok=True)

    etp_path = cwd.parent / "ETP - ESTUDO TÉCNICO PRELIMINAR"  # / "static" / "arquivos_gerados"
    etp_path.mkdir(parents=True, exist_ok=True)

    with st.form("doc_inputs", border=False, clear_on_submit=False):
        col1, col2 = st.columns(2)

        with col1:
            dfd: Path = st.selectbox(
                label="DFD",
                options=[x for x in dfd_path.iterdir() if x.suffix == ".json"],
                accept_new_options=False,
                index=None,
                placeholder="DFD",
                key=st.session_state.dfd_key,
            )

        with col2:
            etp: Path = st.selectbox(
                label="ETP",
                options=[x for x in etp_path.iterdir() if x.suffix == ".json"],
                accept_new_options=False,
                index=None,
                placeholder="ETP",
                key=st.session_state.etp_key,
            )

        # col1, col2, col3 = st.columns(3)
        col1, col2 = st.columns(2)

        with col1:
            # bt_load = st.button(
            bt_load = st.form_submit_button(
                label="Carregar Informaçoes",
                icon=":material/upload:",
                type="primary",
                use_container_width=True,
            )

        with col2:
            bt_clean = st.form_submit_button(
                label="Limpar Campos",
                icon=":material/delete:",
                type="primary",
                use_container_width=True,
            )

        if bt_clean:
            st.session_state.dfd_key = uuid.uuid4()
            st.session_state.etp_key = uuid.uuid4()
            st.session_state.lista_itens.clear()

        dfd_dados = None
        etp_dados = None

        if bt_load:
            if dfd:
                st.info(f"DFD: {dfd}")

                with dfd.open(mode="r", encoding="utf-8") as f:
                    dfd_dados = json.load(f)

            if etp:
                st.info(f"ETP: {etp}")

                with etp.open(mode="r", encoding="utf-8") as f:
                    etp_dados = json.load(f)

            if dfd_dados:
                uo = "".join([c for c in dfd_dados["unidade_orcamentaria"] if c.isdecimal()])

                st.session_state.unit_orc = f"{uo[:-3]}.{uo[-3:]}"

                st.session_state.unidade_solicitante = dfd_dados["setor"]
                st.session_state.dot_nat_desp = dfd_dados["elemento_despesa"]
                st.session_state.dot_acao = dfd_dados["projeto_atividade"]
                st.session_state.dot_subacao = dfd_dados["subacao"]
                st.session_state.dot_programa = dfd_dados["programa"]
                st.session_state.dot_fonte = dfd_dados["fonte"]
                st.session_state.dot_etapa = dfd_dados["etapa"]

                st.session_state.obj_sint = dfd_dados["objetivo"]
                st.session_state.just_qtd = dfd_dados["justificativa"]

                if dfd_dados["tipo_objeto"] == "Material de consumo":
                    st.session_state.tipo_despesa = tipos_despesa[TD.CONSUMO.value]
                elif dfd_dados["tipo_objeto"] == "Material permanente":
                    st.session_state.tipo_despesa = tipos_despesa[TD.EQUIP_APOIO.value]
                elif dfd_dados["tipo_objeto"] == "Equipamento de TI":
                    st.session_state.tipo_despesa = tipos_despesa[TD.EQUIP_TI.value]
                else:
                    st.session_state.tipo_despesa = None

            if etp_dados:
                for i in etp_dados["lista_de_itens"]:
                    item = len(st.session_state.lista_itens) + 1
                    if dfd_dados:
                        for x in dfd_dados["lista_itens"]:
                            if x["catmat"] == i["catmat"]:
                                item = int(x["item"])
                                break

                    st.session_state.lista_itens.append(
                        Itens(
                            item,
                            int(i["catmat"]),
                            i["unidade"],
                            int(i["qtd"]),
                            i["descricao"],
                            float(i["valor_unitario"]),
                        )
                    )
            # else:
            #     if not dfd:
            #         st.warning("Selecione o DFD")
            #     if not etp:
            #         st.warning("Selecione o ETP")
        if len(st.session_state.lista_itens):
            with st.container(border=True):
                st.subheader("Itens Carregados do DFD/ETP (Editar Se Necessario)", anchor=False)
                df = pd.DataFrame(st.session_state.lista_itens)
                st.data_editor(
                    data=df,
                    hide_index=True,
                    column_config={
                        "item": st.column_config.NumberColumn("Item", format="plain"),
                        "cod_siag": st.column_config.NumberColumn("Codigo SIAG"),
                        "unidade": st.column_config.Column("UN"),
                        "qtd": st.column_config.NumberColumn("Quantidade", format="plain"),
                        "descricao": st.column_config.Column("Descriçao"),
                        "valor_un": st.column_config.NumberColumn("Valor Unitario (R$)", format="accounting"),
                    },
                    num_rows="dynamic",
                    key="valores_editados",
                )

        with st.container(border=True):
            st.subheader("Informações Primárias da Contratação", anchor=False)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.number_input(
                    "ISFD Nº",
                    min_value=1,
                    key="numero_isfd",
                )

            with col2:
                st.number_input(
                    "Ano",
                    min_value=2020,
                    key="ano_isfd",
                )

            with col3:
                st.text_input(
                    "Unidade Orçamentaria",
                    placeholder="XX.XXX",
                    key="unit_orc",
                )

            st.selectbox(
                "Tipo De Despesa",
                placeholder="Selecione Um Tipo De Despesa",
                accept_new_options=False,
                options=tipos_despesa,
                key="tipo_despesa",
            )

            st.text_input(
                "Unidade Solicitante",
                placeholder="Coordenadoria De Tecnologia Da Informação",
                key="unidade_solicitante",
            )

            st.text_input(
                "Licitação que originou a ARP",
                placeholder="XXXX Nº XXX/XXXX/XXXXX-MT",
                key="licitacao_origem",
            )

            st.text_input(
                "Ata de Registro de Preço",
                placeholder="Ata de Registro de Preços Nº XXX/XXXX/XXXXX-MT",
                key="ata_registro",
            )

            st.text_input(
                "Data de publicação da ARP",
                placeholder="Edição do Diário Oficial Nº XX.XXX e Publicada em XX de XXXXX de XXXX",
                key="data_publicacao_arp",
            )

            with st.container(border=True):
                st.subheader("Data de vigência da ARP", anchor=False)
                col1, col2 = st.columns(2)

                with col1:
                    st.date_input(
                        "Inicio",
                        key="data_arp_inicio",
                        value="today",
                        format="DD/MM/YYYY",
                    )

                with col2:
                    st.date_input(
                        "Final",
                        key="data_arp_final",
                        value="today",
                        format="DD/MM/YYYY",
                    )

        with st.container(border=True):
            st.subheader("Fundamentação Para Contratação", anchor=False)
            st.text_area(
                "Objeto Sintético",
                key="obj_sint",
                placeholder="Definição do objeto a ser contratado.",
            )

            st.text_area(
                "Justificativa Técnica Para Os Quantitativos/Contratação",
                key="just_qtd",
                placeholder="Justificativa da necessidade da contratação e do porquê do quantitativo solicitado, como serão alocados os equipamentos/serviços, informando como se chegou ao quantitativo almejado, evitando-se justificativas genéricas e preferencialmente com a apresentação de dados que comprovem a quantidade a ser contratada.",
            )
        with st.container(border=True):
            st.subheader("Entrega e Execução", anchor=False)
            col1, col2 = st.columns(2)

            with col1:
                st.number_input(
                    "Prazo de Entrega (Dias Úteis)",
                    placeholder="Dias Úteis",
                    min_value=1,
                    value=None,
                    key="prazo_entrega",
                )

                st.number_input(
                    "Prazo de Vigencia (Meses)",
                    placeholder="Meses",
                    min_value=1,
                    value=None,
                    key="prazo_vigencia",
                )

            with col2:
                st.number_input(
                    "Prazo de Correção (Dias Úteis)",
                    placeholder="Dias Úteis",
                    min_value=1,
                    value=None,
                    key="prazo_correcao",
                )

                st.number_input(
                    "Prazo de Execução (Meses)",
                    placeholder="Meses",
                    min_value=1,
                    value=None,
                    key="prazo_execucao",
                )

            st.checkbox(
                "O Prazo De Vigência Poderá Ser Prorrogado, Enquanto Houver Necessidade Pública, Por Consenso Entre As Partes E Mediante Termo Aditivo",
                key="prorrogar_vigencia",
            )
            st.checkbox(
                "O Prazo De Execução Poderá Ser Prorrogado Dentro Da Vigência Contratual",
                key="prorrogar_execucao",
            )

        with st.container(border=True):
            st.subheader("Fiscalização", anchor=False)
            col1, col2 = st.columns([3, 1])
            with col1:
                st.text_input(
                    "Fiscal Titular",
                    placeholder="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                    key="fiscal_titular",
                )

                st.text_input(
                    "Fiscal Substituto",
                    placeholder="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                    key="fiscal_subs",
                )

                st.text_input(
                    "Gestor Titular",
                    placeholder="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                    key="gestor_titular",
                )

                st.text_input(
                    "Gestor Substituto",
                    placeholder="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                    key="gestor_subs",
                )

            with col2:
                st.text_input(
                    "Matricula",
                    key="fisc_tit_mat",
                    placeholder="XXXXXX",
                )

                st.text_input(
                    "Matricula",
                    key="fisc_sub_mat",
                    placeholder="XXXXXX",
                )

                st.text_input(
                    "Matricula",
                    key="gest_tit_mat",
                    placeholder="XXXXXX",
                )

                st.text_input(
                    "Matricula",
                    key="gest_sub_mat",
                    placeholder="XXXXXX",
                )

        with st.container(border=True):
            st.subheader("Dotação Orçamentária", anchor=False)
            col1, col2, col3 = st.columns(3)

            with col1:
                st.text_input(
                    "Projeto/Atividade",
                    key="dot_acao",
                )

                st.text_input(
                    "Nat. da Despesa",
                    key="dot_nat_desp",
                )

            with col2:
                st.text_input(
                    "Programa",
                    key="dot_programa",
                )

                st.text_input(
                    "Fonte",
                    key="dot_fonte",
                )

            with col3:
                st.text_input(
                    "Subação",
                    key="dot_subacao",
                )

                st.text_input(
                    "Etapa",
                    key="dot_etapa",
                )

        with st.container(border=True):
            st.subheader("Plano de Contrataçao Anual", anchor=False)

            st.checkbox(
                "A Demanda Foi Devidamente Prevista No Plano De Contratações Anual",
                key="previsao_PCA",
                value=True,
            )

            st.text_area(
                "Justificativa de nao previsao",
                placeholder="A Justificativa Padrão Será 'Não Se Aplica.'.\nVocê Pode Alterá-La Se Necessário.",
                key="previsao_PCA_just",
            )

        with st.container(border=True):
            st.subheader("Documentos Necessarios à Instrução", anchor=False)
            st.checkbox(
                "Previsão de Consumo",
                key="previsao_consumo",
            )
            st.checkbox(
                "Parecer de Governança de TIC",
                key="parecer_gov_tic",
            )
            st.checkbox(
                "Comprovação da Vantajosidade e Análise Crítica",
                key="comp_vant_ac",
            )
            st.checkbox(
                "Ofício de Aceite da Empresa",
                key="oficio_empresa",
            )
            st.checkbox(
                "Ofício de Aceite do Órgão Gerenciador",
                key="oficio_og",
            )

        with st.container(border=True):
            st.subheader("Demandante", anchor=False)
            col1, col2 = st.columns(2)

            with col1:
                st.text_input(
                    "Nome",
                    key="demandante_nome",
                    placeholder="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                )
                st.text_input(
                    "Cargo",
                    key="demandante_cargo",
                    placeholder="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                )
            with col2:
                st.text_input(
                    "Matricula",
                    key="demandante_mat",
                    placeholder="XXXXXX",
                )
                st.text_input(
                    "Setor",
                    key="demandante_setor",
                    placeholder="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                )

        with st.container(border=True):
            st.subheader("Diretoria De Administração Sistêmica", anchor=False)
            col1, col2 = st.columns(2)

            with col1:
                st.text_input(
                    "Nome",
                    key="das_nome",
                    placeholder="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                )
                st.text_input(
                    "Cargo",
                    key="das_cargo",
                    placeholder="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                )
            with col2:
                st.text_input(
                    "Matricula",
                    key="das_mat",
                    placeholder="XXXXXX",
                )
                st.text_input(
                    "Setor",
                    key="das_setor",
                    placeholder="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                )

        # if st.session_state.lista_itens:
        #     st.dataframe(
        #         st.session_state.lista_itens,
        #         hide_index=True,
        #         column_config={
        #             "item": st.column_config.NumberColumn("Item", format="%03d"),
        #             "cod_siag": st.column_config.NumberColumn("Codigo SIAG"),
        #             "unidade": st.column_config.Column("UN"),
        #             "qtd": st.column_config.NumberColumn("Quantidade", format="plain"),
        #             "descricao": st.column_config.Column("Descriçao", width="medium"),
        #             "valor_un": st.column_config.NumberColumn("Valor Unitario (R$)", format="accounting"),
        #         },
        #     )

        submit = st.form_submit_button(
            label="Gerar ISFD",
            icon=":material/input:",
            type="primary",
            use_container_width=True,
        )

        if submit:
            print("Submit ----------------------------------")
            if st.session_state.unit_orc:
                unit_orc = group_str("".join([x for x in st.session_state.unit_orc if x.isdecimal()]), 3)
            else:
                unit_orc = ""

            if not st.session_state.previsao_PCA:
                just = st.session_state.previsao_PCA_just.strip()
                if not len(just):
                    st.warning("Justificativa Nao Pode Estar Vazia.")
                previsao_PCA_just = just
            else:
                previsao_PCA_just = "Não Se Aplica."

            if st.session_state.data_arp_inicio > st.session_state.data_arp_final:
                st.error(f"Data final de ARP menor que data inicial: {st.session_state.data_arp_final - st.session_state.data_arp_inicio}")

            context["numero_ISFD"] = st.session_state.numero_isfd
            context["ano"] = st.session_state.ano_isfd
            context["unit_orc"] = unit_orc

            try:
                context["td"] = TD(tipos_despesa.index(st.session_state.tipo_despesa))
            except BaseException:
                context["td"] = TD(0)

            context["unidade_solicitante"] = st.session_state.unidade_solicitante
            context["licitacao_origem"] = st.session_state.licitacao_origem
            context["ata_registro"] = st.session_state.ata_registro
            context["data_publicacao_arp"] = st.session_state.data_publicacao_arp
            context["data_limite_arp"] = f"{st.session_state.data_arp_inicio.strftime('%d/%m/%Y')} a {st.session_state.data_arp_final.strftime('%d/%m/%Y')}"

            context["obj_sint"] = st.session_state.obj_sint
            context["just_qtd"] = st.session_state.just_qtd

            # st.write(st.session_state.valores_editados)
            # st.write(st.session_state.valores_editados["edited_rows"])
            # st.write(st.session_state.valores_editados["added_rows"])
            # st.write(st.session_state.valores_editados["deleted_rows"])

            if "valores_editados" in st.session_state:
                for k, v in st.session_state.valores_editados["edited_rows"].items():
                    print(f"{k = } {v = }")
                    for k2, v2 in v.items():
                        setattr(st.session_state.lista_itens[k], k2, v2)

                for i in st.session_state.valores_editados["added_rows"]:
                    st.session_state.lista_itens.append(Itens(i["item"], i["cod_siag"], i["unidade"], i["qtd"], i["descricao"], i["valor_un"]))

                for i in sorted(st.session_state.valores_editados["deleted_rows"], reverse=True):
                    st.session_state.lista_itens.pop(i)

            context["lista_itens"] = st.session_state.lista_itens

            total_aquisicao = 0.0

            for x in st.session_state.lista_itens:
                vt = x.valor_un * x.qtd
                total_aquisicao += vt

            context["total_aquisicao"] = total_aquisicao
            context["total_aquisicao_escrito"] = dinheiro_para_string(total_aquisicao).upper()

            context["local_entrega"] = (
                "O objeto deverá ser entregue, mediante agendamento de data e hora, nos "
                "dias e horários de expediente desta Autarquia (segunda à sexta-feira das 08h00min às 16h00min), com "
                "comunicação antecipada de 24 (vinte e quatro) horas, na Gerência de Material e Mobiliário do Detran/MT, "
                "situado na Av. Dr. Hélio Ribeiro Torquato da Silva, nº 1000 - Centro Político Administrativo - "
                "CEP 78.048-910 - Cuiabá/MT;"
            )

            context["prazo_entrega"] = st.session_state.prazo_entrega if st.session_state.prazo_entrega else 0
            context["prazo_correcao"] = st.session_state.prazo_correcao if st.session_state.prazo_correcao else 0
            context["vigencia_meses"] = st.session_state.prazo_vigencia if st.session_state.prazo_vigencia else 0
            context["prorrogar_vigencia"] = st.session_state.prorrogar_vigencia
            context["prorrogar_execucao"] = st.session_state.prorrogar_execucao

            context["tem_execucao"] = st.session_state.prazo_execucao is not None
            context["execucao_meses"] = st.session_state.prazo_execucao if st.session_state.prazo_execucao else 0

            context["fiscal_titular"] = st.session_state.fiscal_titular
            context["fiscal_titular_matricula"] = st.session_state.fisc_tit_mat

            context["fiscal_subs"] = st.session_state.fiscal_subs
            context["fiscal_subs_matricula"] = st.session_state.fisc_sub_mat

            context["gestor_titular"] = st.session_state.gestor_titular
            context["gestor_titular_matricula"] = st.session_state.gest_tit_mat

            context["gestor_subs"] = st.session_state.gestor_subs
            context["gestor_subs_matricula"] = st.session_state.gest_sub_mat

            context["dot_nat_desp"] = st.session_state.dot_nat_desp
            context["dot_acao"] = st.session_state.dot_acao
            context["dot_programa"] = st.session_state.dot_programa
            context["dot_subacao"] = st.session_state.dot_subacao
            context["dot_fonte"] = st.session_state.dot_fonte
            context["dot_etapa"] = st.session_state.dot_etapa

            context["previsto_plano"] = st.session_state.previsao_PCA
            context["justificativa_nao_planejada"] = previsao_PCA_just

            context["previsao_consumo"] = st.session_state.previsao_consumo
            context["parecer_gov_tic"] = st.session_state.parecer_gov_tic
            context["comp_vant_ac"] = st.session_state.comp_vant_ac
            context["oficio_empresa"] = st.session_state.oficio_empresa
            context["oficio_og"] = st.session_state.oficio_og

            context["demandante_nome"] = st.session_state.demandante_nome
            context["demandante_cargo"] = st.session_state.demandante_cargo
            context["demandante_mat"] = st.session_state.demandante_mat
            context["demandante_setor"] = st.session_state.demandante_setor

            context["das_nome"] = st.session_state.das_nome
            context["das_cargo"] = st.session_state.das_cargo
            context["das_mat"] = st.session_state.das_mat
            context["das_setor"] = st.session_state.das_setor

            context["data_isfd"] = datetime.now().strftime("Cuiabá-MT, %d de %B de %Y.")

            pprint(context, indent=4)

            for k, v in context.items():
                if v is None:
                    log(LogLevel.WARN, f'Key "{k}" is None')

            output_name = f"ISFD_{context['numero_ISFD']}-{context['ano']}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"

            docx_path = output_path / f"{output_name}.docx"
            json_path = output_path / f"{output_name}.json"

            tpl.render(context, jinja_env)
            tpl.save(docx_path)

            if tpl.is_saved and docx_path.exists() and docx_path.is_file():
                log(LogLevel.INFO, f'Arquivo "{docx_path}" Salvo com sucesso...')
            else:
                log(LogLevel.ERROR, f'Erro ao salvar arquivo "{docx_path}"')

            with json_path.open(mode="w", encoding="utf-8") as f:
                json.dump(context, f, indent=4, sort_keys=True, ensure_ascii=False, cls=CustomEncoder)

            if json_path.exists() and json_path.is_file():
                log(LogLevel.INFO, f'Arquivo "{json_path}" Salvo com sucesso...')
            else:
                log(LogLevel.ERROR, f'Erro ao salvar arquivo "{json_path}"')

# with st.form("itens_siag"):
#     st.text_input(
#         "Termo De Busca",
#         key="test_itens_siag",
#     )
#     sb = st.form_submit_button("Buscar No SIAG")
#     cl = st.form_submit_button("Limpar Lista")
#     if cl:
#         st.session_state.lista_itens.clear()
#     if sb:
#         termo = st.session_state.test_itens_siag.strip()
#         if len(termo):
#             rst = buscar_siag_selenium(termo)
#             st.dataframe(rst)

if docx_path and docx_path.exists():
    with docx_path.open("rb") as f:
        st.download_button(
            "📥 Baixar Documento ISFD",
            data=f,
            file_name=docx_path.name,
            mime=r"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

# with st.container(border=True):
#     itens: list[Itens] = []

#     itens.append(Itens(len(itens) + 1, randint(100000, 999999), "UN", 10, "Descriçao Aleatoria", 50.45))
#     itens.append(Itens(len(itens) + 1, randint(100000, 999999), "UN", 20, "Descriçao Aleatoria", 12.99))
#     itens.append(Itens(len(itens) + 1, randint(100000, 999999), "UN", 8, "Descriçao Aleatoria", 99.99))
#     itens.append(Itens(len(itens) + 1, randint(100000, 999999), "UN", 3, "Descriçao Aleatoria", 15.0))
#     itens.append(Itens(len(itens) + 1, randint(100000, 999999), "UN", 10, "Descriçao Aleatoria", 169.99))

#     st.dataframe(
#         itens,
#         hide_index=True,
#         column_config={
#             "item": st.column_config.NumberColumn("Item", format="plain"),
#             "cod_siag": st.column_config.NumberColumn("Codigo SIAG"),
#             "unidade": st.column_config.Column("UN"),
#             "qtd": st.column_config.NumberColumn("Quantidade", format="plain"),
#             "descricao": st.column_config.Column("Descriçao"),
#             "valor_un": st.column_config.NumberColumn("Valor Unitario (R$)", format="accounting"),
#         },
#     )
