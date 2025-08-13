@echo off
echo 🚀 Iniciando Dashboard de Monitoramento - Mais Correios
echo ======================================================

REM Navegar para o diretório do projeto Flask
cd maiscorreios-monitor

REM Verificar se o ambiente virtual existe
if not exist "venv" (
    echo ❌ Ambiente virtual não encontrado.
    echo 📋 Execute primeiro: install.bat
    pause
    exit /b 1
)

REM Ativar ambiente virtual
echo 🔧 Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Verificar se as dependências estão instaladas
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Dependências não encontradas.
    echo 📋 Execute primeiro: install.bat
    pause
    exit /b 1
)

echo ✅ Ambiente configurado
echo.
echo 🌐 Iniciando servidor Flask na porta 5001...
echo 📊 Dashboard disponível em: http://localhost:5001
echo.
echo 📋 Funcionalidades disponíveis:
echo    • Monitoramento de URLs (automático a cada 10 min)
echo    • Dashboard em tempo real
echo    • Gráfico consolidado de performance
echo    • Monitoramento sintético (fluxo de compra)
echo.
echo ⚠️  Para parar o servidor, pressione Ctrl+C
echo.

REM Iniciar o servidor Flask
python src/main.py

