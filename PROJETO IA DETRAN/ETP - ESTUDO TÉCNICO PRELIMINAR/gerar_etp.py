# gerar_etp.py
from docxtpl import DocxTemplate
from datetime import datetime
from gerar_ia_etp import (
    gerar_justificativa_necessidade_ia,
    gerar_analise_mercado_ia,
    gerar_requisitos_tecnicos_ia,
    gerar_resultados_pretendidos_ia,
    gerar_impactos_ambientais_ia
)
import os
import json

def gerar_etp_completo(dados_gerais, lista_de_itens):
    """
    Gera o Estudo Técnico Preliminar completo e um arquivo .json com os dados.
    
    Retorna:
        tuple: Uma tupla contendo o caminho para o arquivo .docx gerado (str)
               e os dados de contexto em formato de string JSON (str).
    """
    caminho_template = r"C:\Users\pedrosilva\Desktop\PROJETO IA DETRAN\ETP - ESTUDO TÉCNICO PRELIMINAR\templates\template ETP.docx"

    try:
        doc = DocxTemplate(caminho_template)
    except Exception as e:
        print(f"Erro ao carregar o template '{caminho_template}': {e}")
        raise

    # 1. Gera todos os textos complexos e processa os dados primeiro
    # ... (toda a sua lógica de geração de IA e formatação de itens permanece igual)
    justificativa_necessidade_ia = gerar_justificativa_necessidade_ia(dados_gerais['finalidade_geral'])
    analise_mercado_ia = gerar_analise_mercado_ia(dados_gerais['solucoes_alternativas'], dados_gerais['solucao_escolhida'])
    requisitos_tecnicos_ia = gerar_requisitos_tecnicos_ia(dados_gerais['requisitos_tecnicos'])
    resultados_pretendidos_ia = gerar_resultados_pretendidos_ia(dados_gerais['finalidade_geral'])
    impactos_ambientais_ia = gerar_impactos_ambientais_ia(dados_gerais['impactos_ambientais'])
    
    for item in lista_de_itens:
        try:
            valor_unitario = float(item.get('valor_unitario', '0').replace('R$ ', '').replace('.', '').replace(',', '.'))
            quantidade = int(item.get('qtd', '0').replace('.', ''))
            item['valor_unitario_formatado'] = f"R$ {valor_unitario:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ',')
            item['valor_total_formatado'] = f"R$ {(valor_unitario * quantidade):,.2f}".replace('.', 'X').replace(',', '.').replace('X', ',')
        except (ValueError, TypeError):
            item['valor_unitario_formatado'] = "N/A"
            item['valor_total_formatado'] = "N/A"

    # 2. Cria um dicionário "fonte de dados" com TODAS as informações disponíveis
    fonte_de_dados = {
        'etp_numero': dados_gerais['etp_numero'],
        'area_requisitante': dados_gerais['area_requisitante'],
        'responsavel': dados_gerais['responsavel'],
        'subacao_input': dados_gerais['subacao'],
        'etapa_input': dados_gerais['etapa'],
        'natureza_despesa_input': dados_gerais['elemento_despesa'],
        'fonte_input': dados_gerais['fonte'],
        'justificativa_parcelamento_input': dados_gerais['justificativa_parcelamento'],
        'providencias_input': dados_gerais['providencias'],
        'correlatas_input': dados_gerais['correlatas'],
        'viabilidade': dados_gerais['viabilidade'],
        'data_final': dados_gerais['data_final'],
        'elaborador_nome': dados_gerais['elaborador_nome'],
        'elaborador_matricula': dados_gerais['elaborador_matricula'],
        'lista_de_itens': lista_de_itens,
        'descricao_solucao_ia': dados_gerais['descricao_solucao'],
        'projetoatividade': dados_gerais.get('projetoatividade'),
        'programa': dados_gerais.get('programa'),
        'justificativa_necessidade_ia': justificativa_necessidade_ia,
        'analise_mercado_ia': analise_mercado_ia,
        'requisitos_tecnicos_ia': requisitos_tecnicos_ia,
        'resultados_pretendidos_ia': resultados_pretendidos_ia,
        'impactos_ambientais_ia': impactos_ambientais_ia,
    }

    # 3. Obtém as variáveis do template e cria o contexto final dinamicamente
    variaveis_template = doc.get_undeclared_template_variables()
    context = {}
    for var in sorted(variaveis_template):
        valor = fonte_de_dados.get(var)
        context[var] = valor
    
    # Renderiza o documento com o contexto criado dinamicamente
    doc.render(context)

    # Define os nomes dos arquivos
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nome_base_arquivo = f"ETP_Gerado_{timestamp}"
    nome_arquivo_docx = f"{nome_base_arquivo}.docx"
    nome_arquivo_json = f"{nome_base_arquivo}_DATA.json" 

    # --- INÍCIO DAS MODIFICAÇÕES ---

    # ADICIONADO: Converte o dicionário de contexto para uma string JSON formatada para o retorno
    json_string_output = json.dumps(context, indent=4, ensure_ascii=False)

    # Salva o arquivo JSON no disco (lógica existente)
    try:
        # A lógica de salvar o arquivo no disco foi mantida
        with open(nome_arquivo_json, 'w', encoding='utf-8') as f:
            f.write(json_string_output) # Reutiliza a string JSON já criada
    except Exception as e:
        print(f"Erro ao salvar o arquivo JSON '{nome_arquivo_json}': {e}")

    # Salva o arquivo DOCX
    doc.save(nome_arquivo_docx)

    # ALTERADO: Retorna tanto o caminho do DOCX quanto a string JSON
    return nome_arquivo_docx, json_string_output
    
    # --- FIM DAS MODIFICAÇÕES ---