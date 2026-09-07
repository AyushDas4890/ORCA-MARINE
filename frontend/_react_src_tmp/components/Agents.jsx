import { motion } from 'framer-motion'

const AGENTS = [
  { n: '01', name: 'Controller', desc: 'Routes every query to the right specialist, applies session-memory fallback, and refuses to answer when nothing can be grounded.', status: 'Live' },
  { n: '02', name: 'Weather Agent', desc: 'Live weather and marine wave height from Open-Meteo (free, no key). Falls back to mock data on failure — and says so.', status: 'Live' },
  { n: '03', name: 'Ocean Analytics Agent', desc: 'Fishing zones, chlorophyll, sea surface temperature. INCOIS has no public API — runs on labelled mock data until that changes.', status: 'Mock' },
  { n: '04', name: 'Geospatial Agent', desc: "Maritime boundary lookup is live (Marine Regions). MPA geofencing is mock — WDPA's real shapefiles sit behind a registration-gated API token.", status: 'Mixed' },
  { n: '05', name: 'Data Discovery Agent', desc: 'The one place every live call, fallback, and evidence stamp actually happens. The other agents never touch a data source directly.', status: 'Live' },
  { n: '06', name: 'Memory / Session Agent', desc: 'Resolves follow-up questions like "what about the wind speed?" using the prior turn — never overrides an explicit new topic.', status: 'Live' },
  { n: '07', name: 'Reporting Agent', desc: 'Renders a self-contained HTML report with a Leaflet map and full evidence table for every grounded answer.', status: 'Live' },
  { n: '08', name: 'Risk Assessment Agent', desc: 'Synthesizes weather, ocean, and geospatial signal into one deterministic hazard score. No new data source needed.', status: 'Live' },
]

const STATUS_COLOR = {
  Live: 'text-[var(--color-accent)]',
  Mock: 'text-amber-600',
  Mixed: 'text-amber-600',
}

const row = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 110, damping: 20 } },
}

export default function Agents() {
  return (
    <section id="agents" className="bg-zinc-50 px-5 py-20 sm:px-8 sm:py-32">
      <div className="mx-auto flex max-w-[1400px] flex-col gap-12 sm:gap-16">
        <div className="flex items-center gap-3">
          <span className="h-2 w-2 shrink-0 rounded-full bg-[var(--color-accent)]" />
          <p className="m-0 text-xs font-semibold tracking-[0.16em] text-[var(--color-accent)] uppercase sm:text-sm">
            The Roster
          </p>
        </div>

        <h2 className="m-0 max-w-[22ch] text-4xl leading-[0.96] font-semibold uppercase sm:text-7xl lg:text-8xl">
          Eight Agents
          <br />
          One Grounded
          <br />
          Answer
        </h2>

        <motion.div
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, amount: 0.1 }}
          transition={{ staggerChildren: 0.06 }}
          className="flex flex-col divide-y divide-zinc-300"
        >
          {AGENTS.map((a) => (
            <motion.div
              key={a.n}
              variants={row}
              className="grid grid-cols-1 gap-3 py-8 sm:grid-cols-[64px_1fr_100px] sm:items-start sm:gap-8"
            >
              <span className="text-sm font-semibold tracking-wide text-zinc-400">{a.n}</span>
              <div className="flex flex-col gap-2">
                <h3 className="m-0 text-xl font-semibold uppercase sm:text-2xl">{a.name}</h3>
                <p className="m-0 max-w-[62ch] text-base leading-relaxed text-zinc-600">{a.desc}</p>
              </div>
              <span className={`text-[11px] font-bold tracking-[0.12em] uppercase sm:text-right ${STATUS_COLOR[a.status]}`}>
                {a.status}
              </span>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
