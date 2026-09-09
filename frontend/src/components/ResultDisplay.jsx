export default function ResultDisplay({ result }) {
  const isGrounded = result.grounded !== false

  return (
    <section className="mt-12 space-y-6">
      {/* Grounding Badge */}
      <div className={`p-4 rounded-lg border ${isGrounded 
        ? 'bg-green-500/10 border-green-500/50' 
        : 'bg-yellow-500/10 border-yellow-500/50'
      }`}>
        <div className="flex items-center gap-2">
          <span className={`text-xl ${isGrounded ? '✓' : '⚠'}`}></span>
          <span className={`font-semibold ${isGrounded ? 'text-green-300' : 'text-yellow-300'}`}>
            {isGrounded ? 'Grounded Answer' : 'Unable to Ground'}
          </span>
        </div>
        {!isGrounded && (
          <p className="text-sm text-yellow-200 mt-1">
            No agents could provide a grounded answer for this query.
          </p>
        )}
      </div>

      {/* Intent Detection */}
      {result.intent && (
        <div className="p-4 bg-slate-800/50 border border-blue-400/20 rounded-lg">
          <h3 className="font-semibold text-blue-300 mb-2">Detected Intent</h3>
          <p className="text-slate-300">{result.intent}</p>
        </div>
      )}

      {/* Location */}
      {result.location && (
        <div className="p-4 bg-slate-800/50 border border-blue-400/20 rounded-lg">
          <h3 className="font-semibold text-blue-300 mb-2">📍 Location</h3>
          <p className="text-slate-300">{result.location}</p>
        </div>
      )}

      {/* Main Response */}
      {result.response && (
        <div className="p-6 bg-slate-800/50 border border-blue-400/20 rounded-lg">
          <h3 className="font-semibold text-blue-300 mb-4">ORCA's Response</h3>
          <p className="text-slate-300 whitespace-pre-wrap leading-relaxed">
            {result.response}
          </p>
        </div>
      )}

      {/* Evidence / Sources */}
      {result.evidence && result.evidence.length > 0 && (
        <div className="p-6 bg-slate-800/50 border border-cyan-400/20 rounded-lg">
          <h3 className="font-semibold text-cyan-300 mb-4">📚 Evidence & Sources</h3>
          <div className="space-y-2">
            {result.evidence.map((source, i) => (
              <div key={i} className="text-sm text-slate-300">
                <span className="text-cyan-400 font-semibold">Source {i + 1}:</span> {source}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Report Link */}
      {result.report_url && (
        <div className="p-4 bg-slate-800/50 border border-blue-400/20 rounded-lg">
          <a
            href={result.report_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white font-semibold rounded-lg transition"
          >
            📊 View Full Report (Leaflet Map)
          </a>
        </div>
      )}

      {/* Full Response JSON (for debugging) */}
      <details className="p-4 bg-slate-900/50 border border-slate-600/30 rounded-lg cursor-pointer">
        <summary className="text-sm font-mono text-slate-400 hover:text-slate-300">
          Raw Response JSON
        </summary>
        <pre className="mt-4 p-3 bg-black/50 rounded text-xs text-slate-300 overflow-x-auto">
          {JSON.stringify(result, null, 2)}
        </pre>
      </details>
    </section>
  )
}
