@echo off
ECHO.
ECHO    ======================================================
ECHO      INICIANDO PORTAL GERADOR DE DOCUMENTOS DETRAN-MT
ECHO    ======================================================
ECHO.

ECHO    (1/4) Iniciando o servidor de BACK-END (controlador.py)...
REM MODIFICADO: O parametro /B inicia em background sem prender ou criar uma nova janela.
start "Controlador Backend" /B python controlador.py

ECHO    (2/4) Iniciando o servidor de FRONT-END (http.server)...
REM MODIFICADO: O parametro /B eh a chave para o fechamento automatico.
start "Servidor Frontend" /B python -m http.server 8000

ECHO    (3/4) Aguardando 3 segundos para os servidores ligarem...
timeout /t 3 /nobreak >nul

ECHO    (4/4) Abrindo a interface no seu navegador...
REM Agora abrimos a URL correta do nosso servidor de front-end.
start "" "http://localhost:8000/index.html"
                                            
:: O script fez seu trabalho. O comando 'exit' fecha esta janela imediatamente.
exit