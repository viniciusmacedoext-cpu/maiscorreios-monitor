@echo off
echo 🚀 Instalando Dashboard de Monitoramento - Mais Correios
echo ==================================================

REM Verificar se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado. Por favor, instale Python 3.11 ou superior.
    echo 📥 Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python encontrado
python --version

REM Navegar para o diretório do projeto Flask
cd maiscorreios-monitor

REM Criar ambiente virtual se não existir
if not exist "venv" (
    echo 📦 Criando ambiente virtual...
    python -m venv venv
)

REM Ativar ambiente virtual
echo 🔧 Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Instalar dependências
echo 📥 Instalando dependências Python...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Verificar se Google Chrome está instalado
where chrome >nul 2>&1
if %errorlevel% neq 0 (
    where "C:\Program Files\Google\Chrome\Application\chrome.exe" >nul 2>&1
    if %errorlevel% neq 0 (
        echo ⚠️  Google Chrome não encontrado.
        echo 📥 Por favor, instale o Google Chrome:
        echo    https://www.google.com/chrome/
        echo.
        echo ⚠️  O monitoramento sintético não funcionará sem o Chrome.
    ) else (
        echo ✅ Google Chrome encontrado
    )
) else (
    echo ✅ Google Chrome encontrado
)

REM Criar diretório de screenshots
if not exist "src\screenshots" mkdir src\screenshots

echo.
echo 🎉 Instalação concluída com sucesso!
echo.
echo 📋 Próximos passos:
echo    1. Execute: run.bat
echo    2. Acesse: http://localhost:5001
echo.
echo 📚 Consulte o README.md para mais informações.
pause

