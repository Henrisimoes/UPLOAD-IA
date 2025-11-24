from flask import Flask, jsonify
import subprocess
import os
import sys
from flask_cors import CORS
import atexit
from pathlib import Path

app = Flask(__name__)
CORS(app)

# --- CONFIGURAÇÕES IMPORTANTES ---

# 1. (RECOMENDADO) Encontra o executável do Python que está rodando este script.
#    Isso garante que os subprocessos usem o mesmo ambiente e bibliotecas.

PYTHON_EXECUTABLE = sys.executable
cwd = Path(__file__).resolve().parent.parent

# 2. LISTA DE APLICAÇÕES PARA INICIAR

APPS_PARA_INICIAR = [
    {
        "nome": "DFD",
        "caminho_app": cwd / "DFD - DOCUMENTO DE FORMALIZAÇÃO DE DEMANDA" / "app.py",
        "porta": "8501",
    },
    {
        "nome": "ETP",
        "caminho_app": cwd / "ETP - ESTUDO TÉCNICO PRELIMINAR" / "app.py",
        "porta": "8503",
    },
    {
        "nome": "ISS",
        "caminho_app": cwd / "INSTRUMENTO SIMPLIFICADO DE FORMALIZAÇÃO DE DEMANDA" / "app.py",
        "porta": "8505",
    },
    {
        "nome": "PTS",
        "caminho_app": cwd / "PARECER TÉCNICO SETORIAL - MTI"/ "app_streamlit.py",
        "porta": "8507",
    },
    {
        "nome": "GT",
        "caminho_app": cwd / "GT - Gestão de riscos" / "app.py",
        "porta": "8504",
    },
]

# -----------------------------------------

services_started = False
running_processes = []

@app.route("/start_services")
def start_services():
    global services_started, running_processes
    
    if services_started:
        print("Serviços já foram iniciados anteriormente.")
        return jsonify({"status": "already_running", "message": "Os serviços já foram iniciados."})

    try:
        print("Recebido comando para iniciar os serviços...")
        for app_info in APPS_PARA_INICIAR:
            app_name = app_info['nome']
            app_path = app_info['caminho_app']
            app_port = app_info['porta']

            print(f"Iniciando {app_name} na porta {app_port}...")
            
            if not os.path.exists(app_path):
                print(f"!!! ERRO: O arquivo para '{app_name}' não foi encontrado em: {app_path}")
                continue 

            command = [
                PYTHON_EXECUTABLE,
                "-m", "streamlit", "run",
                app_path,
                "--server.port", app_port,
                "--server.headless=true"
            ]
            
            # Define o diretório de trabalho como a pasta onde o app.py está
            working_directory = os.path.dirname(app_path)
            
            # Define o nome do arquivo de log para capturar saídas e erros
            log_file_path = f"{app_name}_log.txt"
            
            # Abre o arquivo de log para escrita
            log_file = open(log_file_path, 'wb')
            
            # Inicia o processo em segundo plano, sem janela de console
            process = subprocess.Popen(
                command,
                stdout=log_file,
                stderr=log_file,
                cwd=working_directory, # Define o diretório de trabalho
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            running_processes.append(process)
            print(f"-> Comando para '{app_name}' enviado. Logs serão salvos em '{log_file_path}'")

        services_started = True
        print("Todos os comandos de inicialização foram enviados. Serviços estão rodando em segundo plano.")
        return jsonify({"status": "success", "message": "Serviços iniciados em segundo plano com sucesso."})

    except Exception as e:
        print(f"Ocorreu um erro crítico ao tentar iniciar os processos: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
    
@atexit.register
def proc_kill():
    global services_started, running_processes

    if services_started:
        p: subprocess.Popen
        for p in running_processes:
            print(f"Killing process: {p.args}")
            p.kill()

if __name__ == "__main__":
    print("Servidor de Controle (versão final e headless) rodando em http://localhost:5000")
    print("Acesse seu index.html e clique no botão 'Iniciar Serviços'.")
    app.run(port=5000)