import { motion } from 'framer-motion'

const fadeUp = {
  hidden: { opacity: 0, y: 28 },
  show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 100, damping: 20 } },
}

export default function Mission() {
  return (
    <section id="mission" className="bg-white px-5 py-20 sm:px-8 sm:py-32 lg:py-40">
      <motion.div
        initial="hidden"
        whileInView="show"
        viewport={{ once: true, amount: 0.3 }}
        transition={{ staggerChildren: 0.12 }}
        className="mx-auto flex max-w-[1400px] flex-col gap-10 sm:gap-16"
      >
        <motion.div variants={fadeUp} className="flex items-center gap-3">
          <span className="h-2 w-2 shrink-0 rounded-full bg-[var(--color-accent)]" />
          <p className="m-0 text-xs font-semibold tracking-[0.16em] text-[var(--color-accent)] uppercase sm:text-sm">
            The Problem
          </p>
        </motion.div>

        <motion.h2
          variants={fadeUp}
          className="m-0 max-w-[20ch] text-4xl leading-[0.96] font-semibold uppercase sm:text-7xl lg:text-8xl"
        >
          Coasts Don&apos;t
          <br />
          Come With
          <br />
          A Manual
        </motion.h2>

        <motion.div variants={fadeUp} className="grid gap-8 lg:grid-cols-2 lg:gap-16">
          <p className="m-0 max-w-[64ch] text-lg leading-relaxed font-medium text-zinc-700 sm:text-xl">
            A fisherman deciding whether to go out today is working from scattered PDFs, word of
            mouth, and whatever bulletin made it to shore in time. Weather, sea state, fishing
            zones, and maritime boundaries live in different systems, updated on different
            schedules, in different formats &mdash; none of it built for a quick decision at 4&nbsp;a.m.
            before a boat leaves harbor.
          </p>
          <p className="m-0 max-w-[64ch] text-lg leading-relaxed font-medium text-zinc-700 sm:text-xl">
            ORCA Marine puts one question in front of a coordinating layer of AI agents &mdash;
            weather, ocean analytics, geospatial, risk &mdash; each pulling from the live source it
            actually knows, and returns one answer with the evidence attached. Not a guess dressed
            up as one.
          </p>
        </motion.div>

        <motion.div
          variants={fadeUp}
          className="flex items-start gap-5 border-t-2 border-b-2 border-ink py-8 sm:gap-6 sm:py-10"
        >
          <span className="shrink-0 text-3xl leading-none font-semibold text-[var(--color-accent)] sm:text-5xl">
            01
          </span>
          <p className="m-0 text-lg leading-snug font-semibold uppercase sm:text-2xl lg:text-3xl">
            Every answer carries evidence &mdash; source and timestamp. If nothing can be grounded,
            ORCA refuses to answer. It never guesses a forecast, and it never guesses a maritime
            boundary.
          </p>
        </motion.div>
      </motion.div>
    </section>
  )
}
