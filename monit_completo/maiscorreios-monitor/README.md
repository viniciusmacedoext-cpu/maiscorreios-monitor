# Dashboard de Monitoramento - Mais Correios

## 📋 Descrição

Sistema completo de monitoramento para o site da Mais Correios, incluindo:
- **Monitoramento de URLs**: Verificação automática de disponibilidade e performance
- **Monitoramento Sintético**: Simulação completa do fluxo de compra
- **Dashboard em Tempo Real**: Interface moderna com gráficos e estatísticas

## ✨ Funcionalidades

### 🔗 Monitoramento de URLs
- Verificação automática a cada 10 minutos
- 6 URLs pré-configuradas da Mais Correios
- Métricas de tempo de resposta e disponibilidade
- Histórico detalhado de verificações
- Alertas visuais para sites offline

### 📊 Dashboard Interativo
- **Visão Geral**: Status de todas as URLs
- **Gráfico Consolidado**: Performance de todas as URLs em um único gráfico
- **Histórico**: Análise detalhada por URL
- **Estatísticas**: Resumo de performance e uptime

### 🛒 Monitoramento Sintético
- Simulação completa do fluxo de compra
- 6 passos automatizados:
  1. Acesso ao site principal
  2. Login com Google
  3. Busca do produto
  4. Adição ao carrinho
  5. Processo de checkout
  6. Finalização com PIX
- Screenshots de cada passo
- Métricas detalhadas de performance

## 🚀 Como Usar

### Pré-requisitos
- Python 3.11+
- Google Chrome
- Conexão com internet

### Instalação

1. **Extrair o projeto**:
```bash
# Extrair o arquivo ZIP para uma pasta de sua escolha
unzip dashboard-maiscorreios-completo.zip
cd maiscorreios-monitor
```

2. **Instalar dependências**:
```bash
# Linux/macOS
./install.sh

# Windows
install.bat
```

3. **Executar o dashboard**:
```bash
# Linux/macOS
./run.sh

# Windows
run.bat
```

4. **Acessar o dashboard**:
- Abra seu navegador
- Acesse: http://localhost:5001

### Configuração Inicial

O sistema já vem pré-configurado com:
- **URLs monitoradas**: 6 páginas principais da Mais Correios
- **Teste sintético**: Fluxo de compra configurado
- **Credenciais**: Login do Google já configurado
- **Produto**: Bebedouro Electrolux pré-selecionado
- **Endereço**: CEP 06816-250 pré-configurado

## 📱 Interface do Dashboard

### Aba "Visão Geral"
- Lista todas as URLs monitoradas
- Status atual (Online/Offline)
- Tempo de resposta
- Última verificação
- Botões para ações rápidas

### Aba "Gráfico Consolidado"
- Gráfico de linhas com todas as URLs
- Cada URL tem cor distinta
- Controle de período (1h, 6h, 12h, 24h, 48h, 7 dias)
- Resumo de performance detalhado

### Aba "Monitoramento Sintético"
- Estatísticas dos testes sintéticos
- Botão "Executar Teste" para iniciar simulação
- Histórico de execuções
- Detalhamento de cada passo
- Taxa de sucesso e duração

### Aba "Histórico"
- Gráfico de performance individual
- Lista detalhada de verificações
- Filtros por período
- Análise de tendências

## 🔧 Configurações Avançadas

### Modificar URLs Monitoradas
1. Acesse o dashboard
2. Clique em "Adicionar URL"
3. Preencha nome e URL
4. Clique em "Adicionar"

### Personalizar Teste Sintético
Edite o arquivo `src/main.py` na seção de configuração do teste:
```python
test_config = {
    'site_url': 'https://www.maiscorreios.com.br',
    'email': 'seu-email@gmail.com',
    'password': 'sua-senha',
    'product_name': 'Nome do produto',
    'address': {
        'cep': '00000-000',
        'street': 'Sua rua',
        'number': '123'
    }
}
```

### Alterar Frequência de Verificação
Edite o arquivo `src/scheduler.py`:
```python
# Altere de 600 segundos (10 min) para o valor desejado
for _ in range(300):  # 5 minutos
```

## 📊 Métricas e Relatórios

### Estatísticas Disponíveis
- **Total de URLs**: Quantidade de sites monitorados
- **URLs Online/Offline**: Status atual
- **Verificações 24h**: Número de checks realizados
- **Tempo de Resposta**: Médio, mínimo e máximo
- **Uptime**: Percentual de disponibilidade
- **Taxa de Sucesso**: Do monitoramento sintético

### Exportação de Dados
Os dados são armazenados em SQLite (`src/database/app.db`) e podem ser consultados diretamente ou via API REST.

## 🛠️ Solução de Problemas

### Erro "ModuleNotFoundError"
```bash
# Reinstalar dependências
source venv/bin/activate
pip install -r requirements.txt
```

### Chrome não encontrado
```bash
# Ubuntu/Debian
sudo apt-get install google-chrome-stable

# CentOS/RHEL
sudo yum install google-chrome-stable
```

### Porta 5001 em uso
Edite `src/main.py` e altere a porta:
```python
app.run(host='0.0.0.0', port=5002, debug=True)
```

### Teste sintético não executa
1. Verifique se o Chrome está instalado
2. Confirme as credenciais do Google
3. Verifique a conexão com internet
4. Consulte os logs no terminal

## 📁 Estrutura do Projeto

```
maiscorreios-monitor/
├── src/
│   ├── models/              # Modelos do banco de dados
│   │   ├── url_monitor.py   # URLs e verificações
│   │   └── synthetic_monitor.py  # Testes sintéticos
│   ├── routes/              # Rotas da API
│   │   ├── monitor.py       # Endpoints de monitoramento
│   │   └── synthetic.py     # Endpoints sintéticos
│   ├── static/              # Frontend React compilado
│   ├── database/            # Banco SQLite
│   ├── screenshots/         # Screenshots dos testes
│   ├── main.py             # Aplicação principal
│   ├── scheduler.py        # Agendador de verificações
│   └── synthetic_engine.py # Engine de automação
├── venv/                   # Ambiente virtual Python
├── requirements.txt        # Dependências Python
├── install.sh             # Script de instalação (Linux/macOS)
├── install.bat            # Script de instalação (Windows)
├── run.sh                 # Script de execução (Linux/macOS)
├── run.bat                # Script de execução (Windows)
└── README.md              # Esta documentação
```

## 🔄 API REST

### Endpoints de Monitoramento
- `GET /api/urls` - Lista URLs monitoradas
- `POST /api/urls` - Adiciona nova URL
- `DELETE /api/urls/{id}` - Remove URL
- `POST /api/urls/{id}/check` - Verifica URL específica
- `POST /api/check-all` - Verifica todas as URLs
- `GET /api/stats` - Estatísticas gerais

### Endpoints Sintéticos
- `GET /api/synthetic-tests` - Lista testes sintéticos
- `POST /api/synthetic-tests/{id}/execute` - Executa teste
- `GET /api/synthetic-tests/{id}/results` - Resultados do teste
- `GET /api/synthetic-stats` - Estatísticas sintéticas

## 🎯 Casos de Uso

### Monitoramento Básico
1. Acompanhar disponibilidade dos sites
2. Receber alertas de indisponibilidade
3. Analisar tendências de performance
4. Gerar relatórios de uptime

### Monitoramento Avançado
1. Testar fluxos críticos de negócio
2. Validar processo de compra
3. Detectar problemas antes dos usuários
4. Monitorar experiência do cliente

### Análise de Performance
1. Identificar gargalos
2. Comparar performance entre páginas
3. Otimizar tempos de resposta
4. Planejar melhorias de infraestrutura

## 📞 Suporte

Para dúvidas ou problemas:
1. Consulte esta documentação
2. Verifique os logs no terminal
3. Teste as funcionalidades individualmente
4. Confirme as configurações de rede

## 🔒 Segurança

- Credenciais armazenadas localmente
- Comunicação via HTTPS quando possível
- Dados sensíveis não expostos na API
- Screenshots armazenadas localmente

## 📈 Roadmap

Funcionalidades futuras:
- [ ] Notificações por email/SMS
- [ ] Integração com Slack/Teams
- [ ] Relatórios em PDF
- [ ] Dashboard mobile
- [ ] Múltiplos usuários
- [ ] Backup automático

---

**Desenvolvido para monitoramento profissional do site Mais Correios**

