import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, List, ArrowUpRight } from '@phosphor-icons/react'

const LINKS = [
  { href: '#mission', label: 'Mission' },
  { href: '#demo', label: 'Try It' },
  { href: '#agents', label: 'Agents' },
  { href: '#platform', label: 'Platform' },
  { href: '#team', label: 'Team' },
]

const fadeDown = {
  hidden: { opacity: 0, y: -16 },
  show: (i) => ({
    opacity: 1,
    y: 0,
    transition: { delay: 0.06 * i, type: 'spring', stiffness: 140, damping: 18 },
  }),
}

function Logo() {
  return (
    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border-2 border-[var(--color-accent)]">
      <div className="h-2.5 w-2.5 rounded-full bg-[var(--color-accent)]" />
    </div>
  )
}

export default function Nav() {
  const [open, setOpen] = useState(false)

  return (
    <>
      <nav className="relative z-20 flex items-center justify-between px-5 pt-5 sm:px-8 sm:pt-6">
        <motion.div variants={fadeDown} custom={0} initial="hidden" animate="show">
          <Logo />
        </motion.div>

        <div className="hidden items-center gap-8 md:flex">
          {LINKS.map((l, i) => (
            <motion.a
              key={l.href}
              href={l.href}
              variants={fadeDown}
              custom={i + 1}
              initial="hidden"
              animate="show"
              className="text-sm font-semibold tracking-[0.16em] uppercase text-ink transition-opacity hover:opacity-60"
            >
              {l.label}
            </motion.a>
          ))}
        </div>

        <motion.button
          type="button"
          variants={fadeDown}
          custom={LINKS.length + 1}
          initial="hidden"
          animate="show"
          whileTap={{ scale: 0.9 }}
          onClick={() => setOpen(true)}
          aria-label="Open menu"
          aria-expanded={open}
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-ink text-white"
        >
          <List size={16} weight="bold" />
        </motion.button>
      </nav>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 z-50 flex flex-col bg-white px-5 pt-5 pb-8 sm:px-8 sm:pt-6"
          >
            <div className="flex items-center justify-between">
              <Logo />
              <motion.button
                type="button"
                whileTap={{ scale: 0.9 }}
                onClick={() => setOpen(false)}
                aria-label="Close menu"
                className="flex h-9 w-9 items-center justify-center rounded-full bg-ink text-white"
              >
                <X size={16} weight="bold" />
              </motion.button>
            </div>

            <div className="mt-16 flex flex-col gap-8">
              {LINKS.map((l, i) => (
                <motion.a
                  key={l.href}
                  href={l.href}
                  onClick={() => setOpen(false)}
                  initial={{ opacity: 0, x: -12 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.04 * i, type: 'spring', stiffness: 140, damping: 18 }}
                  className="text-3xl font-semibold tracking-tight uppercase"
                >
                  {l.label}
                </motion.a>
              ))}
            </div>

            <motion.a
              href="#demo"
              onClick={() => setOpen(false)}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.24 }}
              className="mt-auto inline-flex items-center gap-2 text-xl font-semibold uppercase tracking-wide text-[var(--color-accent)]"
            >
              Explore ORCA <ArrowUpRight size={22} weight="bold" />
            </motion.a>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
