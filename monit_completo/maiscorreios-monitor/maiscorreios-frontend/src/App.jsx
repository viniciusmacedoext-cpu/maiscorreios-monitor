import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { AlertCircle, CheckCircle, Clock, Globe, Plus, Trash2, RefreshCw, Activity, BarChart3, TrendingUp, Play, ShoppingCart } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import './App.css'

function App() {
  const [urls, setUrls] = useState([])
  const [stats, setStats] = useState({ total_urls: 0, online_urls: 0, offline_urls: 0, checks_last_24h: 0 })
  const [loading, setLoading] = useState(true)
  const [newUrl, setNewUrl] = useState('')
  const [newName, setNewName] = useState('')
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [selectedUrlHistory, setSelectedUrlHistory] = useState([])
  const [selectedUrlId, setSelectedUrlId] = useState(null)
  const [consolidatedData, setConsolidatedData] = useState([])
  const [performanceSummary, setPerformanceSummary] = useState([])
  const [consolidatedPeriod, setConsolidatedPeriod] = useState('24')
  
  // Estados para monitoramento sintético
  const [syntheticTests, setSyntheticTests] = useState([])
  const [syntheticStats, setSyntheticStats] = useState({})
  const [syntheticResults, setSelectedTestResults] = useState([])
  const [syntheticSteps, setSelectedTestSteps] = useState([])

  const API_BASE = import.meta.env.VITE_API_BASE || '/api'
  
  console.log('API_BASE:', API_BASE)
  console.log('Environment:', import.meta.env.MODE)

  // Cores para as linhas do gráfico consolidado
  const chartColors = [
    '#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', 
    '#06b6d4', '#84cc16', '#f97316', '#ec4899', '#6366f1'
  ]

  useEffect(() => {
    fetchUrls()
    fetchStats()
    fetchConsolidatedData()
    fetchPerformanceSummary()
    fetchSyntheticTests()
    fetchSyntheticStats()
    
    // Atualiza a cada 30 segundos
    const interval = setInterval(() => {
      fetchUrls()
      fetchStats()
      fetchConsolidatedData()
      fetchPerformanceSummary()
      fetchSyntheticTests()
      fetchSyntheticStats()
    }, 30000)
    return () => clearInterval(interval)
  }, [consolidatedPeriod])

  const fetchUrls = async () => {
    try {
      const response = await fetch(`${API_BASE}/urls`)
      const data = await response.json()
      setUrls(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error('Erro ao buscar URLs:', error)
      setUrls([])
    } finally {
      setLoading(false)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE}/stats`)
      const data = await response.json()
      setStats({
        total_urls: data?.total_urls || 0,
        online_urls: data?.online_count || 0,
        offline_urls: data?.offline_count || 0,
        checks_last_24h: data?.total_checks_24h || 0
      })
    } catch (error) {
      console.error('Erro ao buscar estatísticas:', error)
      setStats({ total_urls: 0, online_urls: 0, offline_urls: 0, checks_last_24h: 0 })
    }
  }

  const fetchConsolidatedData = async () => {
    try {
      const response = await fetch(`${API_BASE}/overview?hours=${consolidatedPeriod}`)
      const data = await response.json()
      setConsolidatedData(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error('Erro ao buscar dados consolidados:', error)
      setConsolidatedData([])
    }
  }

  const fetchPerformanceSummary = async () => {
    try {
      const response = await fetch(`${API_BASE}/overview?hours=${consolidatedPeriod}`)
      const data = await response.json()
      setPerformanceSummary(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error('Erro ao buscar resumo de performance:', error)
      setPerformanceSummary([])
    }
  }

  const fetchSyntheticTests = async () => {
    try {
      const response = await fetch(`${API_BASE}/synthetic-tests`)
      const data = await response.json()
      setSyntheticTests(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error('Erro ao buscar testes sintéticos:', error)
      setSyntheticTests([])
    }
  }

  const fetchSyntheticStats = async () => {
    try {
      const response = await fetch(`${API_BASE}/synthetic-stats`)
      const data = await response.json()
      setSyntheticStats({
        total_tests: data?.active_tests || 0,
        success_rate: data?.success_rate || 0,
        executions_24h: data?.total_executions || 0,
        avg_duration: data?.avg_duration || 0
      })
    } catch (error) {
      console.error('Erro ao buscar estatísticas sintéticas:', error)
      setSyntheticStats({ total_tests: 0, success_rate: 0, executions_24h: 0, avg_duration: 0 })
    }
  }

  const executeSyntheticTest = async (testId) => {
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE}/synthetic-tests/${testId}/execute`, {
        method: 'POST'
      })
      const data = await response.json()
      alert('Teste sintético iniciado com sucesso! Os resultados aparecerão em breve.')
      // Atualizar dados após alguns segundos
      setTimeout(() => {
        fetchSyntheticTests()
        fetchSyntheticStats()
        fetchTestResults(testId) // Buscar resultados específicos deste teste
      }, 5000)
    } catch (error) {
      console.error('Erro ao executar teste sintético:', error)
      alert('Erro ao executar teste sintético')
    } finally {
      setLoading(false)
    }
  }

  const fetchTestResults = async (testId) => {
    try {
      const response = await fetch(`${API_BASE}/synthetic-tests/${testId}/results`)
      const data = await response.json()
      setSelectedTestResults(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error('Erro ao buscar resultados do teste:', error)
      setSelectedTestResults([])
    }
  }

  const fetchTestSteps = async (testId, resultId) => {
    try {
      const response = await fetch(`${API_BASE}/synthetic-tests/${testId}/results/${resultId}/steps`)
      const data = await response.json()
      setSelectedTestSteps(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error('Erro ao buscar passos do teste:', error)
      setSelectedTestSteps([])
    }
  }

  const addUrl = async () => {
    if (!newUrl || !newName) return

    try {
      const response = await fetch(`${API_BASE}/urls`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          url: newUrl,
          name: newName
        })
      })
      
      const data = await response.json()
      if (data.success) {
        setNewUrl('')
        setNewName('')
        setIsAddDialogOpen(false)
        fetchUrls()
        fetchStats()
      } else {
        alert(data.error)
      }
    } catch (error) {
      console.error('Erro ao adicionar URL:', error)
      alert('Erro ao adicionar URL')
    }
  }

  const deleteUrl = async (urlId) => {
    if (!confirm('Tem certeza que deseja remover esta URL do monitoramento?')) return

    try {
      const response = await fetch(`${API_BASE}/urls/${urlId}`, {
        method: 'DELETE'
      })
      
      const data = await response.json()
      if (data.success) {
        fetchUrls()
        fetchStats()
      } else {
        alert(data.error)
      }
    } catch (error) {
      console.error('Erro ao remover URL:', error)
      alert('Erro ao remover URL')
    }
  }

  const checkAllUrls = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE}/check-all`, {
        method: 'POST'
      })
      
      const data = await response.json()
      if (data.success) {
        fetchUrls()
        fetchStats()
      } else {
        alert(data.error)
      }
    } catch (error) {
      console.error('Erro ao verificar URLs:', error)
      alert('Erro ao verificar URLs')
    } finally {
      setLoading(false)
    }
  }

  const fetchUrlHistory = async (urlId) => {
    try {
      const response = await fetch(`${API_BASE}/urls/${urlId}/history`)
      const data = await response.json()
      if (data.success) {
        setSelectedUrlHistory(data.history)
        setSelectedUrlId(urlId)
      }
    } catch (error) {
      console.error('Erro ao buscar histórico:', error)
    }
  }

  const getStatusBadge = (status) => {
    switch (status) {
      case 'online':
        return <Badge className="bg-green-500 hover:bg-green-600"><CheckCircle className="w-3 h-3 mr-1" />Online</Badge>
      case 'offline':
        return <Badge variant="destructive"><AlertCircle className="w-3 h-3 mr-1" />Offline</Badge>
      default:
        return <Badge variant="secondary"><Clock className="w-3 h-3 mr-1" />Desconhecido</Badge>
    }
  }

  const formatResponseTime = (time) => {
    if (!time) return 'N/A'
    return `${(time * 1000).toFixed(0)}ms`
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Nunca'
    return new Date(dateString).toLocaleString('pt-BR')
  }

  const prepareChartData = (history) => {
    return history.slice().reverse().map((check, index) => ({
      index: index + 1,
      responseTime: check.response_time ? check.response_time * 1000 : 0,
      status: check.status,
      time: new Date(check.checked_at).toLocaleTimeString('pt-BR')
    }))
  }

  const prepareConsolidatedChartData = () => {
    if (!consolidatedData.length) return []

    // Criar um mapa de timestamps únicos
    const timestampMap = new Map()
    
    consolidatedData.forEach(urlData => {
      urlData.data_points.forEach(point => {
        const timestamp = new Date(point.timestamp).getTime()
        if (!timestampMap.has(timestamp)) {
          timestampMap.set(timestamp, { timestamp, time: new Date(point.timestamp).toLocaleTimeString('pt-BR') })
        }
      })
    })

    // Converter para array e ordenar
    const timePoints = Array.from(timestampMap.values()).sort((a, b) => a.timestamp - b.timestamp)

    // Adicionar dados de cada URL
    return timePoints.map(timePoint => {
      const dataPoint = { time: timePoint.time }
      
      consolidatedData.forEach((urlData, index) => {
        const point = urlData.data_points.find(p => 
          new Date(p.timestamp).getTime() === timePoint.timestamp
        )
        dataPoint[urlData.url_name] = point ? point.response_time : null
      })
      
      return dataPoint
    })
  }

  if (loading && urls.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600">Carregando dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center">
                <Globe className="w-8 h-8 mr-3 text-blue-600" />
                Dashboard de Monitoramento - Mais Correios
              </h1>
              <p className="text-gray-600 mt-2">Monitore a disponibilidade e performance dos sites em tempo real</p>
            </div>
            <div className="flex gap-3">
              <Button onClick={checkAllUrls} disabled={loading} variant="outline">
                <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Verificar Agora
              </Button>
              <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
                <DialogTrigger asChild>
                  <Button>
                    <Plus className="w-4 h-4 mr-2" />
                    Adicionar URL
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Adicionar Nova URL</DialogTitle>
                    <DialogDescription>
                      Adicione uma nova URL para monitoramento contínuo
                    </DialogDescription>
                  </DialogHeader>
                  <div className="grid gap-4 py-4">
                    <div className="grid gap-2">
                      <Label htmlFor="name">Nome</Label>
                      <Input
                        id="name"
                        placeholder="Ex: Site Principal"
                        value={newName}
                        onChange={(e) => setNewName(e.target.value)}
                      />
                    </div>
                    <div className="grid gap-2">
                      <Label htmlFor="url">URL</Label>
                      <Input
                        id="url"
                        placeholder="https://exemplo.com"
                        value={newUrl}
                        onChange={(e) => setNewUrl(e.target.value)}
                      />
                    </div>
                  </div>
                  <DialogFooter>
                    <Button onClick={addUrl} disabled={!newUrl || !newName}>
                      Adicionar
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total URLs</CardTitle>
              <Globe className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_urls}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Online</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{stats.online_urls}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Offline</CardTitle>
              <AlertCircle className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{stats.offline_urls}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Verificações (24h)</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.checks_last_24h}</div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList>
            <TabsTrigger value="overview">Visão Geral</TabsTrigger>
            <TabsTrigger value="consolidated">Gráfico Consolidado</TabsTrigger>
            <TabsTrigger value="synthetic">Monitoramento Sintético</TabsTrigger>
            <TabsTrigger value="history">Histórico</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid gap-6">
              {urls.map((url) => (
                <Card key={url.id} className="hover:shadow-md transition-shadow">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-lg">{url.name}</CardTitle>
                        <CardDescription className="mt-1">
                          <a href={url.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                            {url.url}
                          </a>
                        </CardDescription>
                      </div>
                      <div className="flex items-center gap-3">
                        {url.latest_check && getStatusBadge(url.latest_check.status)}
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => fetchUrlHistory(url.id)}
                        >
                          <Activity className="w-4 h-4 mr-1" />
                          Histórico
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => deleteUrl(url.id)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Tempo de Resposta</p>
                        <p className="font-medium">
                          {url.latest_check ? formatResponseTime(url.latest_check.response_time) : 'N/A'}
                        </p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Última Verificação</p>
                        <p className="font-medium">
                          {url.latest_check ? formatDate(url.latest_check.checked_at) : 'Nunca'}
                        </p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Status Code</p>
                        <p className="font-medium">
                          {url.latest_check?.status_code || 'N/A'}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="consolidated" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center">
                      <BarChart3 className="w-5 h-5 mr-2" />
                      Gráfico Consolidado de Performance
                    </CardTitle>
                    <CardDescription>
                      Visualização de todas as URLs em um único gráfico
                    </CardDescription>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Label htmlFor="period">Período:</Label>
                    <Select value={consolidatedPeriod} onValueChange={setConsolidatedPeriod}>
                      <SelectTrigger className="w-32">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="1">1 hora</SelectItem>
                        <SelectItem value="6">6 horas</SelectItem>
                        <SelectItem value="12">12 horas</SelectItem>
                        <SelectItem value="24">24 horas</SelectItem>
                        <SelectItem value="48">48 horas</SelectItem>
                        <SelectItem value="168">7 dias</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {consolidatedData.length > 0 ? (
                  <div className="h-96">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={prepareConsolidatedChartData()}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis 
                          dataKey="time" 
                          tick={{ fontSize: 12 }}
                        />
                        <YAxis 
                          label={{ value: 'Tempo de Resposta (ms)', angle: -90, position: 'insideLeft' }}
                        />
                        <Tooltip 
                          labelFormatter={(value) => `Horário: ${value}`}
                          formatter={(value, name) => [
                            value ? `${value.toFixed(0)}ms` : 'N/A', 
                            name
                          ]}
                        />
                        <Legend />
                        {consolidatedData.map((urlData, index) => (
                          <Line 
                            key={urlData.url_id}
                            type="monotone" 
                            dataKey={urlData.url_name} 
                            stroke={chartColors[index % chartColors.length]} 
                            strokeWidth={2}
                            dot={{ fill: chartColors[index % chartColors.length] }}
                            connectNulls={false}
                          />
                        ))}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <div className="text-center text-muted-foreground py-8">
                    <BarChart3 className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>Nenhum dado disponível para o período selecionado</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Performance Summary */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <TrendingUp className="w-5 h-5 mr-2" />
                  Resumo de Performance
                </CardTitle>
                <CardDescription>
                  Estatísticas detalhadas de cada URL no período selecionado
                </CardDescription>
              </CardHeader>
              <CardContent>
                {performanceSummary.length > 0 ? (
                  <div className="space-y-4">
                    {performanceSummary.map((summary) => (
                      <div key={summary.url_id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                        <div>
                          <p className="font-medium">{summary.url_name}</p>
                          <p className="text-sm text-muted-foreground">
                            {summary.total_checks} verificações
                          </p>
                        </div>
                        <div className="grid grid-cols-4 gap-6 text-center">
                          <div>
                            <p className="text-sm text-muted-foreground">Uptime</p>
                            <p className="font-medium text-green-600">
                              {summary.uptime_percentage.toFixed(1)}%
                            </p>
                          </div>
                          <div>
                            <p className="text-sm text-muted-foreground">Tempo Médio</p>
                            <p className="font-medium">
                              {(summary.avg_response_time * 1000).toFixed(0)}ms
                            </p>
                          </div>
                          <div>
                            <p className="text-sm text-muted-foreground">Mínimo</p>
                            <p className="font-medium">
                              {(summary.min_response_time * 1000).toFixed(0)}ms
                            </p>
                          </div>
                          <div>
                            <p className="text-sm text-muted-foreground">Máximo</p>
                            <p className="font-medium">
                              {(summary.max_response_time * 1000).toFixed(0)}ms
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center text-muted-foreground py-8">
                    <TrendingUp className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>Nenhum dado de performance disponível</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="synthetic" className="space-y-6">
            <div className="grid gap-6">
              {/* Estatísticas do Monitoramento Sintético */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Testes Ativos</CardTitle>
                    <ShoppingCart className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{syntheticStats.total_tests || 0}</div>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Taxa de Sucesso</CardTitle>
                    <CheckCircle className="h-4 w-4 text-green-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-green-600">{syntheticStats.success_rate || 0}%</div>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Execuções (24h)</CardTitle>
                    <Activity className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{syntheticStats.executions_24h || 0}</div>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Tempo Médio</CardTitle>
                    <Clock className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{syntheticStats.avg_duration ? Number(syntheticStats.avg_duration).toFixed(0) : 0}s</div>
                  </CardContent>
                </Card>
              </div>

              {/* Lista de Testes Sintéticos */}
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="flex items-center">
                        <ShoppingCart className="w-5 h-5 mr-2" />
                        Testes de Fluxo de Compra
                      </CardTitle>
                      <CardDescription>
                        Monitoramento sintético do processo completo de compra no site da Mais Correios
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  {syntheticTests.length > 0 ? (
                    <div className="space-y-4">
                      {syntheticTests.map((test) => (
                        <div key={test.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                          <div className="flex items-center space-x-4">
                            <div className="flex items-center space-x-2">
                              <ShoppingCart className="w-5 h-5 text-blue-600" />
                              <div>
                                <p className="font-medium">{test.test_name}</p>
                                <p className="text-sm text-muted-foreground">{test.site_url}</p>
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center space-x-4">
                            <div className="text-center">
                              <p className="text-sm text-muted-foreground">Status</p>
                              <Badge className={test.latest_status === 'success' ? 'bg-green-500' : test.latest_status === 'failed' ? 'bg-red-500' : 'bg-yellow-500'}>
                                {test.latest_status === 'success' ? 'Sucesso' : test.latest_status === 'failed' ? 'Falha' : 'Nunca executado'}
                              </Badge>
                            </div>
                            <div className="text-center">
                              <p className="text-sm text-muted-foreground">Última Execução</p>
                              <p className="text-sm font-medium">
                                {test.latest_execution ? formatDate(test.latest_execution) : 'Nunca'}
                              </p>
                            </div>
                            <div className="text-center">
                              <p className="text-sm text-muted-foreground">Duração</p>
                              <p className="text-sm font-medium">
                                {test.latest_duration ? `${test.latest_duration.toFixed(1)}s` : 'N/A'}
                              </p>
                            </div>
                            <Button
                              onClick={() => executeSyntheticTest(test.id)}
                              disabled={loading}
                              className="bg-blue-600 hover:bg-blue-700"
                            >
                              <Play className="w-4 h-4 mr-2" />
                              Executar Teste
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => fetchTestResults(test.id)}
                            >
                              <Activity className="w-4 h-4 mr-1" />
                              Resultados
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center text-muted-foreground py-8">
                      <ShoppingCart className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <p>Nenhum teste sintético configurado</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Resultados dos Testes */}
              {syntheticResults.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Resultados dos Testes Sintéticos</CardTitle>
                    <CardDescription>
                      Histórico de execuções dos testes de fluxo de compra
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {syntheticResults.map((result) => (
                        <div key={result.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                          <div className="flex items-center space-x-4">
                            <Badge className={result.status === 'success' ? 'bg-green-500' : result.status === 'failed' ? 'bg-red-500' : 'bg-yellow-500'}>
                              {result.status === 'success' ? 'Sucesso' : result.status === 'failed' ? 'Falha' : 'Parcial'}
                            </Badge>
                            <div>
                              <p className="font-medium">{formatDate(result.executed_at)}</p>
                              <p className="text-sm text-muted-foreground">
                                {result.steps_completed}/{result.total_steps} passos concluídos
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center space-x-4">
                            <div className="text-center">
                              <p className="text-sm text-muted-foreground">Duração</p>
                              <p className="text-sm font-medium">{result.duration_seconds?.toFixed(1)}s</p>
                            </div>
                            <div className="text-center">
                              <p className="text-sm text-muted-foreground">Taxa</p>
                              <p className="text-sm font-medium">{result.success_rate?.toFixed(1)}%</p>
                            </div>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => fetchTestSteps(result.test_id, result.id)}
                            >
                              Ver Passos
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Passos dos Testes */}
              {syntheticSteps.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Passos da Execução</CardTitle>
                    <CardDescription>
                      Detalhamento de cada passo do teste sintético
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {syntheticSteps.map((step) => (
                        <div key={step.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div className="flex items-center space-x-3">
                            <div className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-100 text-blue-600 text-sm font-medium">
                              {step.step_order}
                            </div>
                            <div>
                              <p className="font-medium">{step.step_name.replace('_', ' ').toUpperCase()}</p>
                              <p className="text-sm text-muted-foreground">
                                {step.duration_seconds?.toFixed(2)}s
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Badge className={step.status === 'success' ? 'bg-green-500' : 'bg-red-500'}>
                              {step.status === 'success' ? 'Sucesso' : 'Falha'}
                            </Badge>
                            {step.error_message && (
                              <p className="text-sm text-red-600 max-w-xs truncate">
                                {step.error_message}
                              </p>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          <TabsContent value="history" className="space-y-6">
            {selectedUrlId ? (
              <Card>
                <CardHeader>
                  <CardTitle>Histórico de Verificações</CardTitle>
                  <CardDescription>
                    Últimas 20 verificações da URL selecionada
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {selectedUrlHistory.length > 0 ? (
                    <div className="space-y-6">
                      <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart data={prepareChartData(selectedUrlHistory)}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="index" />
                            <YAxis />
                            <Tooltip 
                              labelFormatter={(value) => `Verificação ${value}`}
                              formatter={(value) => [`${value.toFixed(0)}ms`, 'Tempo de Resposta']}
                            />
                            <Line 
                              type="monotone" 
                              dataKey="responseTime" 
                              stroke="#3b82f6" 
                              strokeWidth={2}
                              dot={{ fill: '#3b82f6' }}
                            />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                      <div className="space-y-2">
                        {selectedUrlHistory.map((check) => (
                          <div key={check.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <div className="flex items-center space-x-3">
                              {getStatusBadge(check.status)}
                              <span className="text-sm text-muted-foreground">
                                {formatDate(check.checked_at)}
                              </span>
                            </div>
                            <div className="flex items-center space-x-4 text-sm">
                              <span>
                                <strong>Tempo:</strong> {formatResponseTime(check.response_time)}
                              </span>
                              <span>
                                <strong>Status:</strong> {check.status_code || 'N/A'}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="text-center text-muted-foreground py-8">
                      <Activity className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <p>Nenhum histórico disponível</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent className="text-center py-8">
                  <Activity className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p className="text-muted-foreground">
                    Selecione uma URL na aba "Visão Geral" para ver seu histórico
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

export default App

