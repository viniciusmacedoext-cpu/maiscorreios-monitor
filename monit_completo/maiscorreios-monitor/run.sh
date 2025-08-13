#!/bin/bash

echo "🚀 Iniciando Dashboard de Monitoramento - Mais Correios"
echo "======================================================"

# Navegar para o diretório do projeto Flask
cd maiscorreios-monitor

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "❌ Ambiente virtual não encontrado."
    echo "📋 Execute primeiro: ./install.sh"
    exit 1
fi

# Ativar ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Verificar se as dependências estão instaladas
if ! python -c "import flask" 2>/dev/null; then
    echo "❌ Dependências não encontradas."
    echo "📋 Execute primeiro: ./install.sh"
    exit 1
fi

echo "✅ Ambiente configurado"
echo ""
echo "🌐 Iniciando servidor Flask na porta 5001..."
echo "📊 Dashboard disponível em: http://localhost:5001"
echo ""
echo "📋 Funcionalidades disponíveis:"
echo "   • Monitoramento de URLs (automático a cada 10 min)"
echo "   • Dashboard em tempo real"
echo "   • Gráfico consolidado de performance"
echo "   • Monitoramento sintético (fluxo de compra)"
echo ""
echo "⚠️  Para parar o servidor, pressione Ctrl+C"
echo ""

# Iniciar o servidor Flask
python src/main.py

