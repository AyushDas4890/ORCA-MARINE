export default function Hero() {
  return (
    <section className="py-12 text-center">
      <div className="space-y-4 mb-8">
        <h1 className="text-5xl md:text-6xl font-bold">
          <span className="bg-gradient-to-r from-blue-400 via-cyan-400 to-blue-300 bg-clip-text text-transparent">
            Ask ORCA
          </span>
        </h1>
        <p className="text-xl text-slate-300 max-w-2xl mx-auto">
          Agentic AI platform for marine ecosystem reasoning — 8 specialized agents working together to answer your maritime questions with grounded, timestamped evidence.
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-4 mt-12">
        <div className="p-4 bg-blue-500/10 border border-blue-400/30 rounded-lg">
          <h3 className="font-semibold text-blue-300 mb-2">🌊 Live Data</h3>
          <p className="text-sm text-slate-400">Weather, ocean conditions, and maritime boundaries from trusted APIs</p>
        </div>
        <div className="p-4 bg-cyan-500/10 border border-cyan-400/30 rounded-lg">
          <h3 className="font-semibold text-cyan-300 mb-2">🤖 8 Agents</h3>
          <p className="text-sm text-slate-400">Specialized reasoning agents for weather, geospatial, and risk assessment</p>
        </div>
        <div className="p-4 bg-blue-500/10 border border-blue-400/30 rounded-lg">
          <h3 className="font-semibold text-blue-300 mb-2">✓ Grounded</h3>
          <p className="text-sm text-slate-400">Every answer backed by sources and timestamps — or we refuse to answer</p>
        </div>
      </div>
    </section>
  )
}