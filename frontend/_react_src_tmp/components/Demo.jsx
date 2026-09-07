import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowUpRight } from '@phosphor-icons/react'

const API_BASE = 'http://localhost:8000'

const SAMPLES = [
  { label: 'Safe near Chennai?', q: 'Is it safe to venture near Chennai tomorrow?' },
  { label: 'Risk near Kochi?', q: "What's the risk level near Kochi?" },
  { label: 'Fishing zone near Vizag?', q: 'Where is the nearest fishing zone near Visakhapatnam?' },
  { label: 'Restricted zone check?', q: 'Is there a restricted zone near Chennai?' },
]

const sessionId = typeof crypto !== 'undefined' && crypto.randomUUID ? crypto.randomUUID() : String(Date.now())

export default function Demo() {
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  async function ask(query) {
    if (!query || !query.trim()) return
    setText(query)
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: query, session_id: sessionId }),
      })
      if (!res.ok) throw new Error(`Backend responded with HTTP ${res.status}`)
      const data = await res.json()
      setResult(data)
    } catch (err) {
      setResult(null)
      setError(
        `Couldn't reach the ORCA backend at ${API_BASE}. Start it first: uvicorn app.main:app --reload (from the project folder). (${err.message})`
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <section id="demo" className="bg-white px-5 py-20 sm:px-8 sm:py-32">
      <div className="mx-auto flex max-w-[900px] flex-col gap-8 sm:gap-12">
        <div className="flex items-center gap-3">
          <span className="h-2 w-2 shrink-0 rounded-full bg-[var(--color-accent)]" />
          <p className="m-0 text-xs font-semibold tracking-[0.16em] text-[var(--color-accent)] uppercase sm:text-sm">
            Try It
          </p>
        </div>

        <h2 className="m-0 text-3xl leading-none font-semibold uppercase sm:text-6xl">Ask ORCA</h2>

        <p className="m-0 text-base leading-relaxed text-zinc-600 sm:text-lg">
          Ask about weather, fishing zones, maritime boundaries, or overall risk near Chennai, Kochi,
          or Visakhapatnam. This calls the real backend &mdash; it needs to be running locally first (
          <code className="rounded bg-zinc-100 px-1.5 py-0.5">uvicorn app.main:app --reload</code>) on{' '}
          <code className="rounded bg-zinc-100 px-1.5 py-0.5">localhost:8000</code>.
        </p>

        <form
          onSubmit={(e) => {
            e.preventDefault()
            ask(text)
          }}
          className="flex flex-wrap gap-3"
        >
          <input
            value={text}
            onChange={(e) => setText(e.target.value)}
            type="text"
            placeholder="e.g. Is it safe to venture near Chennai tomorrow?"
            autoComplete="off"
            className="flex-1 rounded-full border-2 border-ink px-5 py-4 text-base outline-none min-w-[280px]"
          />
          <motion.button
            type="submit"
            whileTap={{ scale: 0.96 }}
            disabled={loading}
            className="rounded-full bg-ink px-8 py-4 text-sm font-semibold tracking-wide text-white uppercase disabled:opacity-50"
          >
            {loading ? 'Asking...' : 'Ask'}
          </motion.button>
        </form>

        <div className="flex flex-wrap gap-2">
          {SAMPLES.map((s) => (
            <motion.button
              key={s.label}
              type="button"
              whileTap={{ scale: 0.95 }}
              onClick={() => ask(s.q)}
              className="rounded-full bg-[var(--color-accent-soft)] px-4 py-2 text-sm font-semibold text-[var(--color-accent)]"
            >
              {s.label}
            </motion.button>
          ))}
        </div>

        <AnimatePresence mode="wait">
          {result && (
            <motion.div
              key="result"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ type: 'spring', stiffness: 120, damping: 20 }}
              className="flex flex-col gap-4 rounded-2xl border-2 border-ink p-6 sm:p-8"
            >
              <div className="flex flex-wrap items-center gap-2.5">
                <span
                  className="rounded-full px-2.5 py-1 text-[11px] font-bold tracking-wide text-white uppercase"
                  style={{ background: result.grounded ? '#1a7f37' : '#a12a1f' }}
                >
                  {result.grounded ? 'Grounded' : 'Not Grounded'}
                </span>
                <span className="text-[11px] font-bold tracking-wide text-zinc-500 uppercase">
                  Intent: {result.intent} ({result.intent_source})
                </span>
              </div>

              <p className="m-0 text-lg leading-relaxed font-medium">{result.answer}</p>

              {result.evidence?.length > 0 && (
                <div className="flex flex-col gap-2">
                  {result.evidence.map((ev, i) => (
                    <div key={i} className="rounded-lg bg-zinc-50 px-3.5 py-2.5 text-sm leading-snug">
                      <div className="font-semibold">{ev.source}</div>
                      <div className="text-zinc-500">
                        {ev.timestamp}
                        {ev.note ? ` — ${ev.note}` : ''}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {result.report_path && (
                <a
                  href={`${API_BASE}/reports/${encodeURIComponent(result.report_path.split(/[\\/]/).pop())}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex w-fit items-center gap-1.5 text-sm font-semibold tracking-wide text-[var(--color-accent)] uppercase"
                >
                  Open Map Report <ArrowUpRight size={16} weight="bold" />
                </a>
              )}
            </motion.div>
          )}

          {error && (
            <motion.div
              key="error"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              className="rounded-xl bg-[#fdecea] px-5 py-4 text-sm leading-relaxed text-[#a12a1f]"
            >
              {error}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </section>
  )
}
