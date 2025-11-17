import { useState, useEffect } from 'react'
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import Chatbot from './Chatbot'
import NotificationIcon from './NotificationIcon'
import './App.css'

const API_URL = ''

interface DashboardData {
  metrics: {
    total_tasks: number
    overdue_tasks: number
    critical_escalations: number
    alerts: number
    at_risk: number
    avg_completion: number
  }
  risk_distribution: {
    overdue: number
    critical: number
    alert: number
    at_risk: number
    on_track: number
  }
  module_breakdown: Record<string, number>
  overdue_tasks: Task[]
  critical_tasks: Task[]
  alerts_list: Task[]
  dependency_stats: {
    nodes: number
    edges: number
  }
  current_date?: string
}

interface Task {
  task_name: string
  module: string
  mail_id: string
  assigned_to: string
  completion_percent: number
  status: string
  days_overdue?: number
  end_date?: string
}

const COLORS = ['#7f1d1d', '#dc2626', '#f59e0b', '#fbbf24', '#10b981']

function App() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [monitoring, setMonitoring] = useState(false)

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_URL}/api/dashboard-data`)
      if (!response.ok) throw new Error('Failed to fetch data')
      const json = await response.json()
      setData(json)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  const triggerMonitoring = async () => {
    setMonitoring(true)
    try {
      const response = await fetch(`${API_URL}/api/trigger-monitoring`, {
        method: 'POST',
      })
      if (!response.ok) throw new Error('Failed to trigger monitoring')
      await fetchData()
      alert('Monitoring cycle completed successfully!')
    } catch (err) {
      alert(`Error: ${err instanceof Error ? err.message : 'Unknown error'}`)
    } finally {
      setMonitoring(false)
    }
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 60000)
    return () => clearInterval(interval)
  }, [])

  if (loading && !data) {
    return <div className="loading">Loading dashboard...</div>
  }

  if (error && !data) {
    return (
      <div className="app">
        <div className="container">
          <div className="error">Error: {error}</div>
          <button onClick={fetchData} className="btn btn-primary">Retry</button>
        </div>
      </div>
    )
  }

  if (!data) return null

  const riskData = [
    { name: 'Overdue', value: data.risk_distribution.overdue },
    { name: 'Critical', value: data.risk_distribution.critical },
    { name: 'Alert', value: data.risk_distribution.alert },
    { name: 'At Risk', value: data.risk_distribution.at_risk },
    { name: 'On Track', value: data.risk_distribution.on_track },
  ]

  const moduleData = Object.entries(data.module_breakdown).map(([name, value]) => ({
    name: name.length > 20 ? name.substring(0, 20) + '...' : name,
    tasks: value,
  }))

  return (
    <div className="app">
      <div className="header">
        <div className="container">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h1>🤖 Autonomous Project Monitoring Dashboard</h1>
              <p>Real-time monitoring across 5 project modules with AI-powered analysis</p>
            </div>
            <NotificationIcon />
          </div>
        </div>
      </div>

      <div className="container">
        <div className="controls">
          <button onClick={fetchData} className="btn btn-primary" disabled={loading}>
            {loading ? '⟳ Refreshing...' : '🔄 Refresh Data'}
          </button>
          <button onClick={triggerMonitoring} className="btn btn-secondary" disabled={monitoring}>
            {monitoring ? '⟳ Running...' : '▶ Run Monitoring Cycle'}
          </button>
        </div>

        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-label">Total Tasks</div>
            <div className="metric-value">{data.metrics.total_tasks}</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Overdue Tasks</div>
            <div className="metric-value" style={{color: '#7f1d1d'}}>{data.metrics.overdue_tasks}</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Critical Escalations</div>
            <div className="metric-value critical">{data.metrics.critical_escalations}</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Active Alerts</div>
            <div className="metric-value alert">{data.metrics.alerts}</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">At Risk Tasks</div>
            <div className="metric-value alert">{data.metrics.at_risk}</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Avg Completion</div>
            <div className="metric-value success">{data.metrics.avg_completion}%</div>
          </div>
        </div>

        <div className="charts-grid">
          <div className="chart-card">
            <h3 className="chart-title">Risk Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={riskData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {riskData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-card">
            <h3 className="chart-title">Tasks by Module</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={moduleData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="tasks" fill="#667eea" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {data.overdue_tasks && data.overdue_tasks.length > 0 && (
          <div className="table-card">
            <h3 className="chart-title">⏰ Overdue Tasks</h3>
            <table className="table">
              <thead>
                <tr>
                  <th>Task</th>
                  <th>Module</th>
                  <th>Owner</th>
                  <th>Completion</th>
                  <th>Deadline</th>
                  <th>Days Overdue</th>
                </tr>
              </thead>
              <tbody>
                {data.overdue_tasks.map((task, idx) => (
                  <tr key={idx}>
                    <td>{task.task_name}</td>
                    <td>{task.module}</td>
                    <td>{task.mail_id}</td>
                    <td>{task.completion_percent}%</td>
                    <td>{task.end_date || 'N/A'}</td>
                    <td>
                      <span className="badge" style={{backgroundColor: '#7f1d1d'}}>
                        {task.days_overdue || 'N/A'} days
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {data.critical_tasks.length > 0 && (
          <div className="table-card">
            <h3 className="chart-title">🚨 Critical Escalations</h3>
            <table className="table">
              <thead>
                <tr>
                  <th>Task</th>
                  <th>Module</th>
                  <th>Owner</th>
                  <th>Completion</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {data.critical_tasks.map((task, idx) => (
                  <tr key={idx}>
                    <td>{task.task_name}</td>
                    <td>{task.module}</td>
                    <td>{task.mail_id}</td>
                    <td>{task.completion_percent}%</td>
                    <td>
                      <span className="badge badge-critical">
                        {task.days_overdue ? `${task.days_overdue} days overdue` : 'Critical'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {data.alerts_list.length > 0 && (
          <div className="table-card">
            <h3 className="chart-title">⚠️ Active Alerts</h3>
            <table className="table">
              <thead>
                <tr>
                  <th>Task</th>
                  <th>Module</th>
                  <th>Owner</th>
                  <th>Completion</th>
                  <th>Deadline</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {data.alerts_list.map((task, idx) => (
                  <tr key={idx}>
                    <td>{task.task_name}</td>
                    <td>{task.module}</td>
                    <td>{task.mail_id}</td>
                    <td>{task.completion_percent}%</td>
                    <td>{task.end_date || 'N/A'}</td>
                    <td>
                      <span className="badge badge-alert">Alert</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="chart-card">
          <h3 className="chart-title">📊 System Info</h3>
          <p><strong>Current Date:</strong> {data.current_date || new Date().toISOString().split('T')[0]}</p>
          <p><strong>Dependency Graph:</strong> {data.dependency_stats.nodes} nodes, {data.dependency_stats.edges} edges</p>
          <p><strong>Last Update:</strong> {new Date().toLocaleString()}</p>
          <p><strong>Status:</strong> <span style={{color: '#10b981', fontWeight: 600}}>● Operational</span></p>
        </div>
      </div>

      <Chatbot />
    </div>
  )
}

export default App
