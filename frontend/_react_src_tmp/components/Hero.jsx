import { motion } from 'framer-motion'
import { ArrowUpRight } from '@phosphor-icons/react'
import Nav from './Nav.jsx'

const STATS = [
  { value: '8', label: 'AI\nAGENTS' },
  { value: '3', label: 'DATA\nSOURCES' },
  { value: '3', label: 'COASTAL\nREGIONS' },
]

const spring = { type: 'spring', stiffness: 120, damping: 20 }

export default function Hero() {
  return (
    <div className="relative flex min-h-[100dvh] flex-col overflow-hidden">
      <video
        autoPlay
        loop
        muted
        playsInline
        preload="auto"
        poster="/assets/video/poster.jpg"
        className="absolute inset-0 h-full w-full object-cover"
        style={{ zIndex: 0 }}
      >
        <source src="/assets/video/hero-video.mp4" type="video/mp4" />
      </video>

      <Nav />

      <div className="relative z-10 flex flex-1 items-center justify-end px-5 py-8 sm:px-8">
        <div className="flex gap-6 sm:gap-10">
          {STATS.map((s, i) => (
            <motion.div
              key={s.label}
              initial={{ opacity: 0, y: 32 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ ...spring, delay: 0.3 + i * 0.12 }}
              className="text-right"
            >
              <div className="text-2xl leading-none font-semibold sm:text-4xl lg:text-6xl">
                <span className="align-top text-[0.5em] text-[var(--color-accent)]">+</span>
                {s.value}
              </div>
              <div className="mt-1.5 text-[10px] leading-tight font-semibold tracking-[0.16em] uppercase whitespace-pre-line sm:text-xs">
                {s.label}
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      <div className="relative z-10 flex flex-col gap-8 px-5 pb-8 sm:gap-12 sm:px-8 sm:pb-12">
        <div className="flex items-center justify-between gap-4">
          <motion.p
            initial={{ opacity: 0, y: 32 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ ...spring, delay: 0.72 }}
            className="m-0 max-w-[260px] text-[10px] leading-snug font-semibold tracking-[0.16em] uppercase sm:text-sm"
          >
            Charting Safe
            <br />
            Waters Through
            <br />
            Agentic AI
          </motion.p>
          <motion.a
            href="#demo"
            initial={{ opacity: 0, y: 32 }}
            animate={{ opacity: 1, y: 0 }}
            whileTap={{ scale: 0.96 }}
            transition={{ ...spring, delay: 0.86 }}
            className="inline-flex items-center gap-2 text-base font-semibold tracking-[0.12em] uppercase text-[var(--color-accent)] sm:text-2xl"
          >
            Explore ORCA <ArrowUpRight size={22} weight="bold" />
          </motion.a>
        </div>

        <div className="flex items-end justify-between gap-4">
          <motion.p
            initial={{ opacity: 0, y: 32 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ ...spring, delay: 1.0 }}
            className="m-0 w-[120px] shrink-0 text-[9px] leading-snug font-semibold tracking-[0.16em] uppercase sm:w-[260px] sm:text-sm"
          >
            Agentic AI platform built around making ocean intelligence accessible to every fisherman
          </motion.p>
          <h1 className="m-0 text-right text-4xl leading-[0.88] font-semibold uppercase sm:text-7xl lg:text-9xl">
            {['Every', 'Wave', 'Answered'].map((word, i) => (
              <span key={word} className="block overflow-hidden">
                <motion.span
                  className="block"
                  initial={{ y: '110%' }}
                  animate={{ y: 0 }}
                  transition={{ type: 'spring', stiffness: 110, damping: 16, delay: 0.4 + i * 0.14 }}
                >
                  {word}
                </motion.span>
              </span>
            ))}
          </h1>
        </div>
      </div>
    </div>
  )
}
