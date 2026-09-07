import { motion } from 'framer-motion'

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 100, damping: 20 } },
}

export default function Team() {
  return (
    <section id="team" className="bg-white px-5 py-20 sm:px-8 sm:py-32">
      <motion.div
        initial="hidden"
        whileInView="show"
        viewport={{ once: true, amount: 0.4 }}
        transition={{ staggerChildren: 0.1 }}
        className="mx-auto flex max-w-[1400px] flex-col gap-10 sm:gap-16"
      >
        <motion.div variants={fadeUp} className="flex items-center gap-3">
          <span className="h-2 w-2 shrink-0 rounded-full bg-[var(--color-accent)]" />
          <p className="m-0 text-xs font-semibold tracking-[0.16em] text-[var(--color-accent)] uppercase sm:text-sm">
            The Team
          </p>
        </motion.div>

        <motion.h2
          variants={fadeUp}
          className="m-0 max-w-[20ch] text-4xl leading-[0.96] font-semibold uppercase sm:text-7xl lg:text-8xl"
        >
          Built By
          <br />
          One
        </motion.h2>

        <motion.div variants={fadeUp} className="flex flex-wrap items-start justify-between gap-8 sm:gap-16">
          <div className="flex items-center gap-5">
            <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-full border-2 border-[var(--color-accent)] sm:h-22 sm:w-22">
              <div className="h-5 w-5 rounded-full bg-[var(--color-accent)]" />
            </div>
            <div>
              <p className="m-0 text-lg font-semibold uppercase sm:text-2xl">Ayush</p>
              <p className="mt-1 mb-0 text-xs font-semibold tracking-[0.14em] text-zinc-400 uppercase sm:text-sm">
                Solo Builder
              </p>
            </div>
          </div>
          <p className="m-0 max-w-[560px] flex-1 text-base leading-relaxed text-zinc-700 sm:text-lg">
            SIH 2026 requires a 6-member team from one college, with at least one woman on the
            roster, cleared through the college SPOC round. This is currently a one-person build
            &mdash; recruiting the rest of the roster is a submission blocker, not a formality.
          </p>
        </motion.div>
      </motion.div>
    </section>
  )
}
