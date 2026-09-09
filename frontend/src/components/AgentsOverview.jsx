export default function AgentsOverview() {
  const agents = [
    {
      name: 'Controller',
      role: 'Routes queries and enforces grounding',
      emoji: '🎛️',
    },
    {
      name: 'Weather Agent',
      role: 'Wind, waves, marine conditions',
      emoji: '🌊',
    },
    {
      name: 'Ocean Analytics',
      role: 'PFZ, chlorophyll, sea surface temp',
      emoji: '📊',
    },
    {
      name: 'Geospatial Agent',
      role: 'EEZ boundaries & MPA detection',
      emoji: '🗺️',
    },
    {
      name: 'Data Discovery',
      role: 'Unified fetch layer for all agents',
      emoji: '🔍',
    },
    {
      name: 'Memory / Session',
      role: 'Multi-turn conversation context',
      emoji: '💾',
    },
    {
      name: 'Risk Assessment',
      role: 'Hazard scoring (0-6 scale)',
      emoji: '⚠️',
    },
    {
      name: 'Reporting',
      role: 'HTML reports with Leaflet maps',
      emoji: '📋',
    },
  ]

  return (
    <section className="my-16">
      <h2 className="text-3xl font-bold mb-8 text-center">The 8 Specialist Agents</h2>
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
        {agents.map((agent, i) => (
          <div
            key={i}
            className="p-4 bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-blue-400/20 hover:border-blue-400/50 rounded-lg transition"
          >
            <div className="text-3xl mb-2">{agent.emoji}</div>
            <h3 className="font-semibold text-blue-300 mb-1">{agent.name}</h3>
            <p className="text-sm text-slate-400">{agent.role}</p>
          </div>
        ))}
      </div>
    </section>
  )
}