import { motion } from 'framer-motion'

const FACTS = [
  { label: 'Backend', body: <>FastAPI + Pydantic. One <code className="text-white">/query</code> endpoint, typed contracts end to end, 28 pytest tests via dependency injection.</> },
  { label: 'Live Data', body: 'Open-Meteo for weather and wave height. Marine Regions for maritime boundaries. Both free, no key, verified reachable.' },
  { label: 'Gated Data', body: 'INCOIS has no public API. WDPA needs a registration token. Both run on clearly-labelled mock data, never silently faked.' },
  { label: 'Intent Layer', body: 'OpenAI first, keyword rules on failure or no key. Every response reports which path answered — auditable, not hidden.' },
]

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 100, damping: 20 } },
}

export default function Platform() {
  return (
    <section id="platform" className="bg-ink px-5 py-20 text-white sm:px-8 sm:py-32">
      <motion.div
        initial="hidden"
        whileInView="show"
        viewport={{ once: true, amount: 0.3 }}
        transition={{ staggerChildren: 0.1 }}
        className="mx-auto flex max-w-[1400px] flex-col gap-12 sm:gap-16"
      >
        <motion.div variants={fadeUp} className="flex items-center gap-3">
          <span className="h-2 w-2 shrink-0 rounded-full bg-[var(--color-accent)]" />
          <p className="m-0 text-xs font-semibold tracking-[0.16em] text-[var(--color-accent)] uppercase sm:text-sm">
            The Platform
          </p>
        </motion.div>

        <motion.h2
          variants={fadeUp}
          className="m-0 max-w-[22ch] text-4xl leading-[0.96] font-semibold text-white uppercase sm:text-7xl lg:text-8xl"
        >
          Checked,
          <br />
          Not Trusted
          <br />
          On Faith
        </motion.h2>

        <motion.div variants={fadeUp} className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4 lg:gap-10">
          {FACTS.map((f) => (
            <div key={f.label} className="flex flex-col gap-2 border-t border-white/15 pt-5">
              <p className="m-0 text-xs font-bold tracking-[0.14em] text-[var(--color-accent)] uppercase">
                {f.label}
              </p>
              <p className="m-0 text-base leading-relaxed text-zinc-300">{f.body}</p>
            </div>
          ))}
        </motion.div>
      </motion.div>
    </section>
  )
}
