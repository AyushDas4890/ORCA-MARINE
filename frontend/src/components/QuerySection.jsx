import { useState } from 'react'

export default function QuerySection({ onSubmit, loading }) {
  const [query, setQuery] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit(query)
    setQuery('')
  }

  const exampleQueries = [
    'Is it safe to fish off Chennai today?',
    'What are the current ocean conditions near Mumbai?',
    'How deep is the Exclusive Economic Zone off Goa?',
    'Tell me about protected marine areas near the coast',
  ]

  return (
    <section className="my-16">
      <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-blue-500/30 rounded-xl p-8">
        <h2 className="text-2xl font-bold mb-6 text-center">Ask ORCA a Question</h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask about fishing conditions, ocean data, maritime boundaries..."
              className="w-full px-4 py-3 bg-slate-700/50 border border-blue-400/50 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-400/20"
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="w-full py-3 bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 disabled:from-slate-600 disabled:to-slate-600 text-white font-semibold rounded-lg transition transform hover:scale-105 disabled:scale-100"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                Thinking...
              </span>
            ) : (
              'Ask ORCA'
            )}
          </button>
        </form>

        <div className="mt-8">
          <p className="text-sm text-slate-400 mb-3">Try these questions:</p>
          <div className="grid md:grid-cols-2 gap-2">
            {exampleQueries.map((example, i) => (
              <button
                key={i}
                onClick={() => onSubmit(example)}
                disabled={loading}
                className="text-left p-3 bg-slate-700/30 hover:bg-slate-700/50 border border-slate-600/30 rounded-lg text-sm text-slate-300 hover:text-blue-300 transition disabled:opacity-50"
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}