import locale as lc
from pathlib import Path
from datetime import datetime
import json
from dataclasses import dataclass, asdict

import streamlit as st
from PIL import Image
import jinja2
from docxtpl import DocxTemplate
import pandas as pd  # noqa: F401

lc.setlocale(lc.LC_ALL, "C")  # Reset para um locale padrão antes de tentar pt_BR

lc_cat = [lc.LC_CTYPE, lc.LC_TIME, lc.LC_MONETARY]

try:
    for cat in lc_cat:
        lc.setlocale(cat, "pt_BR.UTF-8")
except lc.Error:
    try:
        for cat in lc_cat:
            lc.setlocale(cat, "pt_BR")
    except lc.Error:
        for cat in lc_cat:
            lc.setlocale(cat, "")  # Fallback para o padrão do sistema


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        return super().default(obj)


DATE = datetime.now()
cwd = Path(__file__).resolve().parent

# ========== TÍTULO COM LOGO ==========
logo_path = cwd.parent / "DFD" / "static" / "logo_detran.png"

st.write(f"Streamlit Version: {st.__version__}")
st.set_page_config(layout="wide")

st.markdown('<div class="title-container">', unsafe_allow_html=True)

if logo_path.exists():
    logo = Image.open(logo_path)
    st.image(logo, width=60)
else:
    st.warning(f"Logo não encontrada em: {logo_path}. Verifique o caminho.")

st.markdown('<div class="title-text">Gerador de Gestao de Riscos - DETRAN-MT</div>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

input_path = (cwd / "template" / "Template-GR.docx").resolve()
output_path = (cwd / "output").resolve()

output_path.mkdir(parents=True, exist_ok=True)

if not input_path.exists():
    raise FileNotFoundError(f'Arquivo de template nao encontrado em "{input_path}"')

jinja_env = jinja2.Environment()

tpl = DocxTemplate(input_path)

context: dict = dict.fromkeys(tpl.get_undeclared_template_variables(jinja_env))


riscos = [
    "Identificação incorreta, imprecisa ou insuficiente da necessidade pública a ser atendida com a contratação.",  # A 0
    "Descrição incorreta, imprecisa ou insuficiente do objeto da contratação.",  # B 1
    "Erros na elaboração do orçamento estimativo.",  # C 2
    "Definição incorreta ou inadequada dos requisitos de habilitação técnica ou de habilitação econômico-financeira.",  # D 3
    "Estabelecimento de condições de participação que restrinjam de modo injustificado o universo de potenciais licitantes.",  # E 4
    "Decisões ou escolhas sem a devida e suficiente motivação.",  # F 5
    "Definição incorreta, imprecisa ou insuficiente dos encargos contratuais",  # G 6
    "Defeitos no controle da execução contratual ou no recebimento definitivo do objeto.",  # H 7
    "Atraso ou suspensão no processo licitatório em face de impugnações.",  # I 8
    "Descrição insuficiente do modelo de execução do contrato.",  # J 9
    "Ausência de modelo de gestão do contrato ou modelo insuficiente.",  # L 10
]

lbl_fontes = [
    "Nao Consta",
    "Recursos Humanos",
    "Estrutura",
    "Processos De Trabalho",
    "Série Histórica",
    "Prospecção De Cenário",
    "Necessidade Da Parte",
    "Visão De Especialista",
]


lbl_probs = [
    "Raro",  # 0
    "Pouco Provável",  # 1
    "Provével",  # 2
    "Muito Provável",  # 3
    "Praticamente Certo",  # 4
]

lbl_impactos = [
    "Muito Baixo",  # 0
    "Baixo",  # 1
    "Médio",  # 2
    "Alto",  # 3
    "Muito Alto",  # 4
]


def write_center(text: str):
    st.markdown(f"<p style='text-align: center;'>{text}</p>", unsafe_allow_html=True)


if "setor" not in st.session_state:
    st.session_state.setor = "Coordenadoria de Tecnologia da Informação"
if "setor_resp" not in st.session_state:
    st.session_state.setor_resp = "Danilo Vieira da Cruz"

if "A_fonte_tec" not in st.session_state:
    st.session_state.A_fonte_tec = lbl_fontes[1]
    st.session_state.risco_A_desc = riscos[0]
    st.session_state.risco_A_fda = "Planejamento da contratação"
    st.session_state.risco_A_prob = lbl_probs[1]
    st.session_state.risco_A_imp = lbl_impactos[1]
    st.session_state.risco_A_danos = [
        "Desperdício de recursos humanos no processo licitatório.",
        "Falha na especificação da necessidade pública a ser atendida com a contratação.",
    ]
    st.session_state.risco_A_trat = "Mitigar"

    st.session_state.acao_prev_A_acao1 = "Revisar a especificação da necessidade pública a ser atendida com a contratação."
    st.session_state.acao_prev_A_resp1 = "Danilo Vieira da Cruz\nAnderson Freitas de Magalhães"

    st.session_state.acao_cont_A_acao1 = "Elaborar a ERRATA ou a nova especificação da necessidade pública a ser atendida com a contratação."
    st.session_state.acao_cont_A_resp1 = "Danilo Vieira da Cruz\nAnderson Freitas de Magalhães"

if "B_fonte_tec" not in st.session_state:
    st.session_state.B_fonte_tec = lbl_fontes[1]
    st.session_state.risco_B_desc = riscos[1]
    st.session_state.risco_B_fda = "Planejamento da contratação"
    st.session_state.risco_B_prob = lbl_probs[1]
    st.session_state.risco_B_imp = lbl_impactos[1]
    st.session_state.risco_B_danos = [
        "Desperdício de recursos humanos no processo licitatório.",
        "Objeto de contratação errado que pode causar impugnações e licitação deserta.",
    ]
    st.session_state.risco_B_trat = "Mitigar"

    st.session_state.acao_prev_B_acao1 = "Realizar pesquisa de mercado para conhecer os produtos disponíveis e suas funções."
    st.session_state.acao_prev_B_resp1 = "Danilo Vieira da Cruz\nAnderson Freitas de Magalhães"

    st.session_state.acao_cont_B_acao1 = "Analisar as impugnações no edital e providenciar as correções."
    st.session_state.acao_cont_B_resp1 = "Danilo Vieira da Cruz\nAnderson Freitas de Magalhães"


if "C_fonte_tec" not in st.session_state:
    st.session_state.C_fonte_tec = lbl_fontes[1]
    st.session_state.risco_C_desc = riscos[2]
    st.session_state.risco_C_fda = "Planejamento da contratação"
    st.session_state.risco_C_prob = lbl_probs[1]
    st.session_state.risco_C_imp = lbl_impactos[1]
    st.session_state.risco_C_danos = [
        "Desperdício de recursos humanos no processo licitatório.",
        "Atraso no processo de aquisição.",
    ]
    st.session_state.risco_C_trat = "Mitigar"

    st.session_state.acao_prev_C_acao1 = "Realizar ampla pesquisa de preço obedecendo a orientação normativa específica para tal fim."
    st.session_state.acao_prev_C_resp1 = "Danilo Vieira da Cruz\nAnderson Freitas de Magalhães"

    st.session_state.acao_prev_C_acao2 = "Considerar custos com frete e instalação quando for o caso."
    st.session_state.acao_prev_C_resp2 = "Danilo Vieira da Cruz\nAnderson Freitas de Magalhães"

    st.session_state.acao_cont_C_acao1 = "Redefinir as especificações da solução a ser adquirida."
    st.session_state.acao_cont_C_resp1 = "Danilo Vieira da Cruz\nAnderson Freitas de Magalhães"

if "J_fonte_tec" not in st.session_state:
    st.session_state.J_fonte_tec = lbl_fontes[1]
    st.session_state.risco_J_desc = riscos[9]
    st.session_state.risco_J_fda = "Planejamento da contratação"
    st.session_state.risco_J_prob = lbl_probs[2]
    st.session_state.risco_J_imp = lbl_impactos[3]
    st.session_state.risco_J_danos = [
        "Desperdício de recursos humanos no processo licitatório.",
        "Atraso no processo de aquisição.",
    ]
    st.session_state.risco_J_trat = "Mitigar"

    st.session_state.acao_prev_J_acao1 = "Conferência e controle da conformidade do procedimento com utilização de checklist."
    st.session_state.acao_prev_J_resp1 = "Danilo Vieira da Cruz\nAnderson Freitas de Magalhães"

    st.session_state.acao_prev_J_acao2 = (
        "Descrever o modelo de execução do objeto contendo: descrição da "
        "dinâmica do contrato, definição do método para quantificar a execução do "
        "objeto contratado, definição do formato e do conteúdo do instrumento "
        "formal que será utilizado nas etapas de solicitação, acompanhamento, "
        "fiscalização e recebimento do objeto."
    )
    st.session_state.acao_prev_J_resp2 = "Coordenadoria de TI"

    st.session_state.acao_cont_J_acao1 = "Questionar a área demandante quanto ao modelo de execução do objeto para definir o regime de execução da contratação."
    st.session_state.acao_cont_J_resp1 = "Danilo Vieira da Cruz\nAnderson Freitas de Magalhães"


if "L_fonte_tec" not in st.session_state:
    st.session_state.L_fonte_tec = lbl_fontes[1]
    st.session_state.risco_L_desc = riscos[10]
    st.session_state.risco_L_fda = "Planejamento da contratação"
    st.session_state.risco_L_prob = lbl_probs[2]
    st.session_state.risco_L_imp = lbl_impactos[3]
    st.session_state.risco_L_danos = [
        "Gestão e fiscalização inadequada do contrato.",
        "Não manutenção das condições de habilitação exigidas na contratação.",
        "Subjetividade na avaliação da conformidade do objeto.",
    ]
    st.session_state.risco_L_trat = "Mitigar"

    st.session_state.acao_prev_L_acao1 = "Capacitar pessoal ou designar pessoal capacitado para executar a atividade de gestão e fiscalização do contrato."
    st.session_state.acao_prev_L_resp1 = "Coordenadoria de TI"

    st.session_state.acao_prev_L_acao2 = (
        "Incluir no modelo de gestão a definição de protocolo de comunicação entre contratante e contratada ao longo da execução contratual."
    )
    st.session_state.acao_prev_L_resp2 = "Coordenadoria de TI"

    st.session_state.acao_prev_L_acao3 = "Inserir cláusula contratual de manutenção das condições de habilitação."
    st.session_state.acao_prev_L_resp3 = "Danilo Vieira da Cruz\nAnderson Freitas de Magalhães"

    st.session_state.acao_cont_L_acao1 = "Utilizar modelo de gestão padrão com indicação dos responsáveis pela gestão."
    st.session_state.acao_cont_L_resp1 = "Danilo Vieira da Cruz\nAnderson Freitas de Magalhães"


if "riscos_usados" not in st.session_state:
    st.session_state.riscos_usados = {}


with st.container(border=True):
    st.subheader("Carregar Dados do DFD (Opcional)", anchor=False)

    dfd_path = cwd.parent / "DFD" / "static" / "arquivos_gerados"
    dfd_path.mkdir(parents=True, exist_ok=True)

    with st.form("doc_inputs", border=False, clear_on_submit=False):
        st.selectbox(
            label="DFD",
            options=[x for x in dfd_path.iterdir() if x.suffix == ".json"],
            accept_new_options=False,
            index=None,
            placeholder="DFD",
            key="dfd_path",
        )

        bt_load = st.form_submit_button(
            label="Carregar Informaçoes",
            icon=":material/upload:",
            type="primary",
            use_container_width=True,
        )

        dfd: Path = st.session_state.dfd_path
        if bt_load and dfd:
            with dfd.open(mode="r", encoding="utf-8") as f:
                dfd_dados = json.load(f)

            if dfd_dados:
                st.session_state.obj_sint = dfd_dados["objetivo"].strip()

                st.session_state.setor = dfd_dados["setor"].strip()
                st.session_state.setor_resp = dfd_dados["responsavel"].strip()


with st.container(border=True):
    st.subheader("Area Requisitante", anchor=False)
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Area Requisitante", key="setor")
    with col2:
        st.text_input("Responsavel", key="setor_resp")

with st.container(border=True):
    st.subheader("Objeto Da Contratação", anchor=False)
    st.text_area(
        "obj_sint",
        key="obj_sint",
        label_visibility="collapsed",
        height=200,
    )

with st.container(border=True):
    st.subheader("Responsável Pela Elaboração", anchor=False)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.text_input(
            "Elaborador",
            key="elaborador",
        )
    with col2:
        st.text_input(
            "Matricula",
            key="elaborador_mat",
        )


grid_size = [2, 18, 12]
with st.container(border=True):
    with st.container(border=True):
        col1, col2, col3 = st.columns(grid_size, vertical_alignment="center")
        with col1:
            write_center("Alíneas")
        with col2:
            write_center("Riscos<br>(Decreto Estadual 1525/2022, art. 327, inciso VII, alíneas A a H)")
        with col3:
            col31, col32 = st.columns([3, 4], vertical_alignment="center")
            with col31:
                write_center("Fontes")
            with col32:
                write_center("Tecnicas")
    offset = 65
    for c, risco in enumerate(riscos):
        if chr(offset + c) == "K":
            offset += 1
        with st.container(border=True):
            col1, col2, col3 = st.columns(grid_size, vertical_alignment="center")
            with col1:
                write_center(f"{offset + c:c}")
            with col2:
                st.write(risco)
            with col3:
                st.radio(
                    chr(offset + c),
                    options=lbl_fontes,
                    horizontal=True,
                    label_visibility="collapsed",
                    key=f"{offset + c:c}_fonte_tec",
                )


def add_acao_fields(c, i, tipo):
    # print(f"{c = }, {i = }, {tipo = }")
    col1, col2 = st.columns(
        [8, 4],
        vertical_alignment="center",
    )
    with col1:
        st.text_area(
            "Açao",
            key=f"acao_{tipo}_{c}_acao{i}",
            # label_visibility="collapsed",
        )
    with col2:
        st.text_area(
            "Responsavel",
            key=f"acao_{tipo}_{c}_resp{i}",
            # label_visibility="collapsed",
        )


def add_acao2(c: str):
    if f"acao_prev_{c}_count" not in st.session_state:
        st.session_state[f"acao_prev_{c}_count"] = 1
        while f"acao_prev_{c}_acao{st.session_state[f'acao_prev_{c}_count']}" in st.session_state:
            st.session_state[f"acao_prev_{c}_count"] += 1

    with st.container(border=True):
        col1, col2 = st.columns([2, 1], vertical_alignment="center")
        with col1:
            st.subheader("Açoes Preventivas", anchor=False)
        with col2:
            col21, col22 = st.columns(2, vertical_alignment="center")
            with col21:
                if st.button("Adicionar Açao Preventiva", key=f"add_ac_prev_{c}", use_container_width=True):
                    st.session_state[f"acao_prev_{c}_count"] += 1
            with col22:
                if st.button("Remover Açao Preventiva", key=f"del_ac_prev_{c}", use_container_width=True):
                    if st.session_state[f"acao_prev_{c}_count"] > 1:
                        st.session_state[f"acao_prev_{c}_count"] -= 1

        for i in range(st.session_state[f"acao_prev_{c}_count"]):
            add_acao_fields(c, i + 1, "prev")

    if f"acao_cont_{c}_count" not in st.session_state:
        st.session_state[f"acao_cont_{c}_count"] = 1
        while f"acao_cont_{c}_acao{st.session_state[f'acao_cont_{c}_count']}" in st.session_state:
            st.session_state[f"acao_cont_{c}_count"] += 1

    with st.container(border=True):
        col1, col2 = st.columns([2, 1], vertical_alignment="center")
        with col1:
            st.subheader("Açoes de Contingencia", anchor=False)
        with col2:
            col21, col22 = st.columns(2, vertical_alignment="center")
            with col21:
                if st.button("Adicionar Açao de Contingencia", key=f"add_ac_cont_{c}", use_container_width=True):
                    st.session_state[f"acao_cont_{c}_count"] += 1
            with col22:
                if st.button("Remover Açao de Contingencia", key=f"del_ac_cont_{c}", use_container_width=True):
                    if st.session_state[f"acao_cont_{c}_count"] > 1:
                        st.session_state[f"acao_cont_{c}_count"] -= 1

        # print(f'st.session_state[f"acao_cont_{c}_count"] = {st.session_state[f"acao_cont_{c}_count"]}')
        for i in range(st.session_state[f"acao_cont_{c}_count"]):
            add_acao_fields(c, i + 1, "cont")


def add_acao2_unused(c: str):
    st.warning("TODO: Quantidade De Açoes De Acordo Com Escolha Do Usuario")

    if "num_ac_prev" not in st.session_state:
        st.session_state.num_ac_prev = 1
    if "num_ac_cont" not in st.session_state:
        st.session_state.num_ac_cont = 1

    with st.container(border=True):
        col1, col2 = st.columns([0.25, 0.75], vertical_alignment="center")
        with col1:
            st.subheader("Açoes", anchor=False)
        with col2:
            b1 = st.button(
                "Adicionar Açao Preventiva",
                key=f"add_ac_prev_{c}",
                use_container_width=True,
            )
        if b1:
            st.session_state.num_ac_prev += 1
        for i in range(st.session_state.num_ac_prev):
            with st.container(border=False):
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.subheader("Açao Preventiva", anchor=False)
                with col2:
                    _, col22 = st.columns(2)

                    with col22:
                        b2 = st.button(
                            "Remover Açao Preventiva",
                            key=f"T2_{c}_{i}_prev",
                            use_container_width=True,
                        )
                    if b2:
                        if st.session_state.num_ac_prev > 1:
                            st.session_state.num_ac_prev -= 1

                st.text_area(
                    "Açao",
                    key=f"risco_{c}_ac_prev_{i}",
                    # label_visibility="collapsed",
                )
                st.text_area(
                    "Responsavel",
                    key=f"risco_{c}_ac_prev_{i}_resp",
                    # label_visibility="collapsed",
                )
        # with col2:
        for i in range(st.session_state.num_ac_cont):
            with st.container(border=False):
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.subheader("Açao de Contingencia", anchor=False)
                with col2:
                    _, col22 = st.columns(2)

                    with col22:
                        b2 = st.button(
                            "Remover Açao de Contingencia",
                            key=f"T2_{c}_{i}_cont",
                            use_container_width=True,
                        )
                    if b2:
                        if st.session_state.num_ac_cont > 1:
                            st.session_state.num_ac_cont -= 1

                st.text_area(
                    "Açao",
                    key=f"risco_{c}_ac_cont_{i}",
                    # label_visibility="collapsed",
                )
                st.text_area(
                    "Responsavel",
                    key=f"risco_{c}_ac_cont_{i}_resp",
                    # label_visibility="collapsed",
                )


def make_btn_lambda(c, dn):
    # print(c, dn)
    return lambda: st.session_state[f"risco_{c}_danos"].pop(dn)


if "risco_danos" not in st.session_state:
    st.session_state.risco_danos = dict()


def add_risco2(i: int):
    offset = 65

    if (offset + i) >= ord("K"):
        offset += 1
    c = chr(offset + i)

    with st.expander(f"Risco {c}", expanded=False):
        st.text_input(
            "Descrição",
            key=f"risco_{c}_desc",
        )
        st.text_input(
            "Fase De Analise",
            key=f"risco_{c}_fda",
        )

        col1, col2 = st.columns(2)
        with col1:
            st.selectbox(
                "Probabilidade",
                options=lbl_probs,
                key=f"risco_{c}_prob",
            )
        with col2:
            st.selectbox(
                "Impacto",
                options=lbl_impactos,
                key=f"risco_{c}_imp",
            )

        if f"qtd_danos_{c}" not in st.session_state:
            if f"risco_{c}_danos" not in st.session_state:
                st.session_state[f"risco_{c}_danos"] = []
            st.session_state[f"qtd_danos_{c}"] = len(st.session_state[f"risco_{c}_danos"]) + 1

        with st.container(border=True):
            col1, col2 = st.columns(2, vertical_alignment="center")
            with col1:
                st.subheader("Danos", anchor=False)
            with col2:
                col21, col22 = st.columns(2)
                with col21:
                    st.button("Adicionar Dano", key=f"risco_{c}_add_dano", use_container_width=True)
                with col22:
                    st.button("Remover Ultimo Dano", key=f"risco_{c}_del_dano", use_container_width=True)

            if st.session_state[f"risco_{c}_add_dano"]:
                st.session_state[f"qtd_danos_{c}"] += 1

            if st.session_state[f"risco_{c}_del_dano"]:
                if st.session_state[f"qtd_danos_{c}"] > 1:
                    st.session_state[f"qtd_danos_{c}"] -= 1

            for i, d in enumerate(st.session_state[f"risco_{c}_danos"]):
                if f"risco_{c}_dano_{i}" not in st.session_state:
                    st.session_state[f"risco_{c}_dano_{i}"] = d

            for i in range(st.session_state[f"qtd_danos_{c}"]):
                st.text_input(
                    f"Dano {i + 1}",
                    key=f"risco_{c}_dano_{i}",
                )

            st.text_input(
                "Tratamento",
                key=f"risco_{c}_trat",
            )
        add_acao2(c)


offset = 65
for c in range(len(riscos)):
    if chr(offset + c) == "K":
        offset += 1
    s = f"{offset + c:c}_fonte_tec"
    st.session_state.riscos_usados.update({s: st.session_state[s]})


st.write(f"Riscos: {len([x for x in st.session_state.riscos_usados.values() if x and x != lbl_fontes[0]])}")

# risco_counter = 0
# cols = st.columns(2)
# st.session_state.risco_danos.clear()

for k, v in st.session_state.risco_danos.items():
    # print(k, v)
    # print(st.session_state[k])
    st.session_state[k].remove(v)
    # print(st.session_state[k])

for i, v in enumerate(st.session_state.riscos_usados.values()):
    if v == lbl_fontes[0]:
        continue
    add_risco2(i)

btn_submit = st.button(
    "Submit",
    type="primary",
    use_container_width=True,
)

_ = """
if btn_submit:
    d = dict(st.session_state)
    d["dfd_path"] = str(d["dfd_path"])
    st.json(json.dumps(d, ensure_ascii=False, sort_keys=True))

    context["setor"] = st.session_state.get("setor", "").strip()
    context["setor_resp"] = st.session_state.get("setor_resp", "").strip()
    context["obj_sint"] = st.session_state.get("obj_sint", "").strip()
    context["data"] = DATE.strftime("Cuiabá-MT, %d de %B de %Y.")

    tbl_id_riscos = {
        "Recursos Humanos": "RH",
        "Estrutura": "EST",
        "Processos De Trabalho": "PT",
        "Série Histórica": "SH",
        "Prospecção De Cenário": "PC",
        "Necessidade Da Parte": "NP",
        "Visão De Especialista": "VE",
    }

    offset = 65
    for i in range(len(riscos)):
        if offset + i == ord("K"):
            offset += 1
        for prefix in tbl_id_riscos.values():
            context[f"{prefix}_{offset + i:c}"] = ""

    offset = 65
    for k, v in st.session_state.riscos_usados.items():
        st.write(f"{k = }, {v = }")
        if v == "Nao Consta":
            continue

        context[f"{tbl_id_riscos[v]}_{k[0]}"] = "X"

        # st.write(f'{k2 = }, {v2 = }')
        # st.write(f"{i = }, {c = }")
        # if c == "Nao Consta":
        #     continue
        # if chr(i + offset) == "K":
        #     offset += 1
        # st.write(f"{tbl_id_riscos[c]}_{i + offset:c}")
    offset = 65
    for i in range(len(riscos)):
        if (offset + i) == ord("K"):
            offset += 1
        c = chr(offset + i)
        context[f"danos_{c}"] = []
        if f"qtd_danos_{c}" in st.session_state:
            for j in range(st.session_state[f"qtd_danos_{c}"]):
                context[f"danos_{c}"].append(st.session_state[f"risco_{c}_dano_{j}"])

    st.write("Context")
    st.json(json.dumps(context, ensure_ascii=False, sort_keys=True))

    # st.write("Submitted")

    output_name = f"GR_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"

    docx_path = output_path / f"{output_name}.docx"
    json_path = output_path / f"{output_name}.json"

    tpl.render(context)
    tpl.save(docx_path)

    with json_path.open(mode="w", encoding="utf-8") as f:
        json.dump(context, f, indent=4, sort_keys=True, ensure_ascii=False)

    st.info(f'Arquivo salvo em "{docx_path.resolve()}"')
"""


@dataclass
class Risco:
    def __init__(self, c: str, desc: str, fda: str, prob: str, imp: str, danos: list, trat: str, ap: list, ac: list):
        self.c = c
        self.desc = desc
        self.fda = fda
        self.prob = prob
        self.imp = imp
        self.danos = danos
        self.trat = trat
        self.ap = ap
        self.ac = ac

    def to_dict(self):
        return asdict(self)


@dataclass
class Acao:
    def __init__(self, acao, resp):
        self.acao = acao
        self.resp = resp

    def to_dict(self):
        return asdict(self)


if btn_submit:
    context["setor"] = st.session_state.get("setor", "").strip()
    context["elaborador"] = st.session_state.get("elaborador", "").strip()
    context["elaborador_mat"] = st.session_state.get("elaborador_mat", "").strip()

    context["setor_resp"] = st.session_state.get("setor_resp", "").strip()
    context["setor_resp"] = st.session_state.get("setor_resp", "").strip()

    context["data"] = DATE.strftime("Cuiabá-MT, %d de %B de %Y.")

    context["setor"] = st.session_state.get("setor", "").strip()
    context["setor_resp"] = st.session_state.get("setor_resp", "").strip()
    context["obj_sint"] = st.session_state.get("obj_sint", "").strip()

    context["riscos"] = []
    tbl_id_riscos = {
        "Recursos Humanos": "RH",
        "Estrutura": "EST",
        "Processos De Trabalho": "PT",
        "Série Histórica": "SH",
        "Prospecção De Cenário": "PC",
        "Necessidade Da Parte": "NP",
        "Visão De Especialista": "VE",
    }

    offset = 65
    for i in range(len(riscos)):
        if offset + i == ord("K"):
            offset += 1
        c = chr(offset + i)

        for v in tbl_id_riscos.values():
            context[f"{v}_{c}"] = ""

        if st.session_state[f"{c}_fonte_tec"] != "Nao Consta":
            context[f"{tbl_id_riscos[st.session_state[f'{c}_fonte_tec']]}_{c}"] = "X"

            lap = []
            j = 1
            while f"acao_prev_{c}_acao{j}" in st.session_state:
                a = st.session_state.get(f"acao_prev_{c}_acao{j}", "").strip()
                r = st.session_state.get(f"acao_prev_{c}_resp{j}", "").strip()
                if a and r:
                    lap.append(Acao(a, r))
                j += 1

            lac = []
            j = 1
            while f"acao_cont_{c}_acao{j}" in st.session_state:
                a = st.session_state.get(f"acao_cont_{c}_acao{j}", "").strip()
                r = st.session_state.get(f"acao_cont_{c}_resp{j}", "").strip()
                if a and r:
                    lac.append(Acao(a, r))
                j += 1

            r = Risco(
                c,
                riscos[i],
                st.session_state.get(f"risco_{c}_fda", "").strip(),
                st.session_state.get(f"risco_{c}_prob", "").strip(),
                st.session_state.get(f"risco_{c}_imp", "").strip(),
                st.session_state.get(f"risco_{c}_danos", []),
                st.session_state.get(f"risco_{c}_trat", "").strip(),
                lap,
                lac,
            )

            context["riscos"].append(r)
    for k, v in context.items():
        if v is None:
            st.warning(f"Campo {k} é nulo")

    output_name = f"GR_{DATE.strftime('%Y-%m-%d_%H-%M-%S')}"

    docx_path = output_path / f"{output_name}.docx"
    json_path = output_path / f"{output_name}.json"

    tpl.render(context)
    tpl.save(docx_path)

    with json_path.open(mode="w", encoding="utf-8") as f:
        json.dump(context, f, indent=4, sort_keys=True, ensure_ascii=False, cls=CustomEncoder)

    st.info(f'Arquivo salvo em "{docx_path.resolve()}"')
