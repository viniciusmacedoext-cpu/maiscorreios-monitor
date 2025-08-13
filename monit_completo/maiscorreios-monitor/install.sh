#!/bin/bash

echo "🚀 Instalando Dashboard de Monitoramento - Mais Correios"
echo "=================================================="

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale Python 3.11 ou superior."
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"

# Navegar para o diretório do projeto Flask
cd maiscorreios-monitor

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências
echo "📥 Instalando dependências Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Verificar se Google Chrome está instalado
if ! command -v google-chrome &> /dev/null; then
    echo "⚠️  Google Chrome não encontrado."
    echo "📋 Para instalar no Ubuntu/Debian:"
    echo "   wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -"
    echo "   echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list"
    echo "   sudo apt-get update"
    echo "   sudo apt-get install google-chrome-stable"
    echo ""
    echo "📋 Para instalar no CentOS/RHEL:"
    echo "   sudo yum install google-chrome-stable"
    echo ""
    echo "⚠️  O monitoramento sintético não funcionará sem o Chrome."
else
    echo "✅ Google Chrome encontrado: $(google-chrome --version)"
fi

# Criar diretório de screenshots
mkdir -p src/screenshots

echo ""
echo "🎉 Instalação concluída com sucesso!"
echo ""
echo "📋 Próximos passos:"
echo "   1. Execute: ./run.sh"
echo "   2. Acesse: http://localhost:5001"
echo ""
echo "📚 Consulte o README.md para mais informações."

