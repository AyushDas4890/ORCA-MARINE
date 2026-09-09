import { useState } from 'react'
import Hero from './components/Hero'
import QuerySection from './components/QuerySection'
import AgentsOverview from './components/AgentsOverview'
import ResultDisplay from './components/ResultDisplay'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function App() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleQuery = async (query) => {
    if (!query.trim()) {
      setError('Please enter a question')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch(`${API_URL}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err.message || 'Failed to fetch response from ORCA backend')
      console.error('Query error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleHealthCheck = async () => {
    try {
      const response = await fetch(`${API_URL}/health`)
      if (response.ok) {
        const data = await response.json()
        console.log('Backend health:', data)
        alert('✓ Backend is running')
      } else {
        alert('✗ Backend returned an error')
      }
    } catch (err) {
      alert(`✗ Cannot reach backend at ${API_URL}`)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-blue-900 to-slate-900">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 bg-slate-900/80 backdrop-blur-md border-b border-blue-500/20">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <div className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
              🐋 ORCA Marine
            </div>
          </div>
          <button
            onClick={handleHealthCheck}
            className="px-4 py-2 rounded-lg bg-blue-500/10 hover:bg-blue-500/20 border border-blue-400/50 text-sm font-medium text-blue-300 transition"
          >
            Check Backend
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-12">
        {/* Hero Section */}
        <Hero />

        {/* Agents Overview */}
        <AgentsOverview />

        {/* Query Section */}
        <QuerySection onSubmit={handleQuery} loading={loading} />

        {/* Error Display */}
        {error && (
          <div className="mt-8 p-4 bg-red-500/10 border border-red-500/50 rounded-lg">
            <p className="text-red-300">
              <span className="font-semibold">Error:</span> {error}
            </p>
          </div>
        )}

        {/* Result Display */}
        {result && <ResultDisplay result={result} />}
      </main>

      {/* Footer */}
      <footer className="mt-20 py-8 border-t border-blue-500/20 text-center text-slate-400 text-sm">
        <p>Built for SIH 2026 · ISRO Problem Statement 26176</p>
      </footer>
    </div>
  )
}