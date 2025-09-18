# Em seu arquivo: gerar_doc.py
# Versão Final com Configuração no Topo

import json
import os
import locale as lc
from docxtpl import DocxTemplate
from typing import Dict, Any, Optional

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


# ==============================================================================
# --- CONFIGURAÇÃO DOS ARQUIVOS ---
# Altere os caminhos e nomes dos arquivos nesta seção.
# ==============================================================================

# 1. Caminho para o seu template do Word (.docx)
#    É o modelo que será preenchido.
#    Exemplo Windows: r'C:\Users\SeuUsuario\Documentos\template_word.docx'
#    Exemplo Mac/Linux: '/home/seu_usuario/documentos/template_word.docx'
CAMINHO_TEMPLATE = r'C:\Users\pedrosilva\Desktop\PROJETO IA DETRAN\PARECER TÉCNICO SETORIAL - MTI\templates\template_word.docx'

# 2. Caminho para o seu arquivo de dados JSON
#    É o arquivo que contém as informações para o relatório.
#    Exemplo: r'C:\Users\SeuUsuario\dados\ISFD.json'
CAMINHO_JSON = r'C:\Users\pedrosilva\Desktop\PROJETO IA DETRAN\PARECER TÉCNICO SETORIAL - MTI\ISFD.json'

# 3. Nome do arquivo de saída que será gerado
#    Este será o nome do seu relatório final.
#    Exemplo: r'C:\Users\SeuUsuario\Relatorios\Relatorio_Final.docx'
CAMINHO_SAIDA = r'C:\Users\pedrosilva\Desktop\PROJETO IA DETRAN\PARECER TÉCNICO SETORIAL - MTI\relatorio_gerado.docx'

# --- FIM DA CONFIGURAÇÃO ---
# ==============================================================================


class GeradorRelatorioWord:
    """
    Uma classe robusta para gerar relatórios em .docx a partir de um template
    e dados em formato JSON com validação e tratamento de erros aprimorado.
    """
    
    def __init__(self, caminho_template: str):
        self.template = None
        self.caminho_template = caminho_template
        
        if not self._validar_arquivo_existe(self.caminho_template):
            raise FileNotFoundError(f"Template não encontrado: {self.caminho_template}")
        
        try:
            self.template = DocxTemplate(self.caminho_template)
            print(f"✓ Template '{self.caminho_template}' carregado com sucesso.")
        except Exception as e:
            print(f"✗ ERRO ao carregar o template Word: {e}")
            raise

    def _validar_arquivo_existe(self, caminho: str) -> bool:
        return os.path.exists(caminho) and os.path.isfile(caminho)

    def _validar_estrutura_json(self, dados: Dict[str, Any]) -> bool:
        """
        Valida se o JSON possui a estrutura mínima necessária para o formato ISFD.json.
        """
        campos_obrigatorios = ['ano', 'numero_ISFD', 'obj_sint', 'lista_itens']
        for campo in campos_obrigatorios:
            if campo not in dados:
                print(f"✗ Campo obrigatório ausente no JSON: '{campo}'")
                return False
        
        if not isinstance(dados.get('lista_itens'), list):
            print("✗ 'lista_itens' deve ser uma lista")
            return False
            
        if not dados['lista_itens']:
            print("⚠ Aviso: a lista 'lista_itens' está vazia")
        
        for i, item in enumerate(dados.get('lista_itens', [])):
            campos_item = ['item', 'cod_siag', 'descricao', 'qtd']
            for campo in campos_item:
                if campo not in item:
                    print(f"✗ Campo '{campo}' ausente no item {i+1} da lista 'lista_itens'")
                    return False
        
        print("✓ Estrutura do JSON (ISFD) validada com sucesso")
        return True

    def _carregar_json(self, caminho_json: str) -> Optional[Dict[str, Any]]:
        if not self._validar_arquivo_existe(caminho_json):
            print(f"✗ Arquivo JSON não encontrado: {caminho_json}")
            return None
        
        try:
            with open(caminho_json, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            print(f"✓ JSON '{caminho_json}' carregado com sucesso.")
            
            # Validação removida para permitir JSONs com estrutura diferente
            # if not self._validar_estrutura_json(dados):
            #     return None

            # Adicionar total_aquisicao se existir
            if 'total_aquisicao' in dados:
                dados['total_aquisicao'] = lc.currency(dados['total_aquisicao'], grouping=True)
            return dados
            
        except json.JSONDecodeError as e:
            print(f"✗ Erro ao decodificar JSON: {e}")
            return None
        except Exception as e:
            print(f"✗ Erro inesperado ao carregar JSON: {e}")
            return None

    def gerar_documento(self, caminho_json: str, caminho_saida: str) -> bool:
        """
        Orquestra a geração do relatório.
        """
        print(f"🔄 Iniciando geração do documento...")
        contexto = self._carregar_json(caminho_json)
        if contexto is None:
            print("✗ Falha ao carregar/validar o JSON. Processo interrompido.")
            return False

        try:
            print("🔄 Preenchendo o documento com os dados...")
            self.template.render(contexto)
            print("✓ Template renderizado com sucesso")
        except Exception as e:
            print(f"✗ Erro ao renderizar o template: {e}")
            return False

        try:
            # Garante que o diretório de saída exista
            diretorio_pai = os.path.dirname(caminho_saida)
            if diretorio_pai and not os.path.exists(diretorio_pai):
                os.makedirs(diretorio_pai, exist_ok=True)
            
            self.template.save(caminho_saida)
            print(f"✅ Relatório '{caminho_saida}' gerado com sucesso!")
            return True
        except PermissionError:
            print(f"✗ Erro de permissão ao salvar '{caminho_saida}'. Verifique se o arquivo não está aberto.")
            return False
        except Exception as e:
            print(f"✗ Erro ao salvar o arquivo de saída: {e}")
            return False

# --- SEÇÃO DE EXECUÇÃO ---
# Esta parte do código usa as variáveis que você configurou no topo.
# Não é necessário editar nada aqui.
if __name__ == "__main__":
    print("=" * 70)
    print("--- Iniciando Gerador de Relatório ---")
    print(f"   Template: {CAMINHO_TEMPLATE}")
    print(f"   JSON: {CAMINHO_JSON}")
    print(f"   Saída: {CAMINHO_SAIDA}")
    print("=" * 70)
    
    try:
        # Cria uma instância do gerador
        gerador = GeradorRelatorioWord(CAMINHO_TEMPLATE)

        # Chama o método para gerar o documento
        gerador.gerar_documento(CAMINHO_JSON, CAMINHO_SAIDA)
    
    except FileNotFoundError:
        print(f"\nERRO: O arquivo de template '{CAMINHO_TEMPLATE}' não foi encontrado.")
        print("Por favor, verifique o caminho na seção de configuração no topo do script.")
    except Exception as e:
        print(f"\nOcorreu um erro inesperado no processo: {e}")
    
    print("\n--- Processo Finalizado ---")