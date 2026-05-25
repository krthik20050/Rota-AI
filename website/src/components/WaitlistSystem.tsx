"use client"

import * as React from "react"
import { motion, AnimatePresence } from "framer-motion"
import confetti from "canvas-confetti"
import { Button } from "@/components/ui/button"
import { Copy, Check, Users, ArrowUp, ArrowRight, Loader2 } from "lucide-react"

type UIState = "hero" | "collect_email" | "loading" | "success"

export function WaitlistSystem() {
  const [uiState, setUiState] = React.useState<UIState>("hero")
  const [email, setEmail] = React.useState("")
  const [data, setData] = React.useState<{ code: string; position?: number; referrals?: number } | null>(null)
  const [copied, setCopied] = React.useState(false)
  const [errorMsg, setErrorMsg] = React.useState<string | null>(null)

  // On mount, check if there's a ref in URL
  const [refCode, setRefCode] = React.useState<string | null>(null)
  React.useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const ref = params.get("ref")
    if (ref) setRefCode(ref)
  }, [])

  // Once joined, periodically poll for status
  React.useEffect(() => {
    if (uiState !== "success" || !data?.code) return
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`/api/status?code=${data.code}`)
        const json = await res.json()
        if (json.position) {
          setData(d => d ? { ...d, position: json.position, referrals: json.referrals } : null)
        }
      } catch (err) {}
    }, 5000)
    return () => clearInterval(interval)
  }, [uiState, data?.code])

  const triggerConfetti = () => {
    confetti({
      particleCount: 80,
      spread: 60,
      origin: { y: 0.6 },
      colors: ['#e4f222', '#ffffff', '#8a8f98'],
      disableForReducedMotion: true
    })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email) return

    setUiState("loading")
    setErrorMsg(null)

    try {
      const res = await fetch("/api/join", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, ref: refCode }),
      })

      const json = await res.json()

      if (res.ok) {
        setData({ code: json.code })

        // Fetch initial position optimistically (doesn't block success UI transition)
        fetch(`/api/status?code=${json.code}`).then(res => res.json()).then(statusJson => {
            if(statusJson.position) {
               setData(prev => prev ? { ...prev, position: statusJson.position, referrals: statusJson.referrals } : null)
            }
        }).catch(() => {})

        setUiState("success")
        triggerConfetti()
      } else {
        setUiState("collect_email")
        setErrorMsg(json.error || "Failed to join")
      }
    } catch {
      setUiState("collect_email")
      setErrorMsg("Network error. Try again.")
    }
  }

  const copyLink = () => {
    if (!data?.code) return
    const link = `${window.location.origin}?ref=${data.code}`
    navigator.clipboard.writeText(link)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const variants = {
    initial: { opacity: 0, y: 10, filter: "blur(4px)" },
    animate: { opacity: 1, y: 0, filter: "blur(0px)" },
    exit: { opacity: 0, y: -10, filter: "blur(4px)" }
  }

  return (
    <div className="w-full max-w-xl mx-auto flex flex-col justify-center min-h-[400px]">
      <AnimatePresence mode="wait">

        {uiState === "hero" && (
          <motion.div
            key="hero"
            variants={variants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={{ duration: 0.3, ease: "easeOut" }}
            className="flex flex-col items-center text-center space-y-8"
          >
            <div className="space-y-4">
              <h1 className="text-4xl sm:text-5xl md:text-6xl font-semibold tracking-tighter text-text-primary">
                Rota AI
              </h1>
              <p className="text-text-secondary text-lg max-w-md mx-auto">
                Speak. Transcribe. Clean with AI. Inject into your workflow instantly.
              </p>
            </div>
            <Button onClick={() => setUiState("collect_email")} className="group px-8">
              Join Waitlist
              <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
            </Button>
          </motion.div>
        )}

        {uiState === "collect_email" && (
          <motion.div
            key="collect_email"
            variants={variants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={{ duration: 0.3, ease: "easeOut" }}
            className="flex flex-col items-center text-center space-y-6 w-full max-w-sm mx-auto"
          >
            <div className="space-y-2">
              <h2 className="text-2xl font-semibold tracking-tighter text-text-primary">
                Request Access
              </h2>
              <p className="text-text-secondary text-sm">
                Enter your email to secure your spot.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="w-full space-y-3">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@domain.com"
                required
                autoFocus
                className="w-full h-12 px-4 rounded-md bg-surface-100 border border-border text-text-primary placeholder:text-text-tertiary focus:outline-none focus:ring-1 focus:ring-accent transition-shadow font-mono text-sm"
              />
              <Button type="submit" className="w-full">
                Continue
              </Button>
            </form>
            {errorMsg && (
              <p className="text-sm text-red-500 font-mono">{errorMsg}</p>
            )}
          </motion.div>
        )}

        {uiState === "loading" && (
          <motion.div
            key="loading"
            variants={variants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={{ duration: 0.2 }}
            className="flex flex-col items-center justify-center space-y-4 py-12"
          >
            <Loader2 className="w-8 h-8 text-accent animate-spin" />
            <p className="text-text-secondary font-mono text-sm uppercase tracking-widest">
              Processing
            </p>
          </motion.div>
        )}

        {uiState === "success" && (
          <motion.div
            key="success"
            variants={variants}
            initial="initial"
            animate="animate"
            transition={{ duration: 0.4, ease: "easeOut" }}
            className="flex flex-col items-center text-center space-y-8 p-8 rounded-lg border border-border bg-surface-100 shadow-xl w-full max-w-sm mx-auto"
          >
            <div className="space-y-2">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-accent/10 text-accent mb-2">
                <Check className="w-6 h-6" />
              </div>
              <h2 className="text-2xl font-semibold tracking-tighter text-text-primary">
                You're on the list.
              </h2>
              <p className="text-text-secondary text-sm max-w-[250px] mx-auto">
                Check your email for confirmation.
              </p>
            </div>

            {data?.position ? (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="w-full p-4 rounded-md bg-surface-200 border border-border space-y-1"
              >
                <p className="text-xs text-text-tertiary uppercase tracking-wider font-semibold">Your Position</p>
                <p className="text-4xl font-semibold tracking-tighter text-text-primary flex items-center justify-center gap-2 font-mono">
                  #{data.position.toLocaleString()}
                  {data.referrals ? <span className="text-sm text-accent flex items-center font-sans tracking-normal"><ArrowUp className="w-3 h-3 mr-1"/>Jumped</span> : null}
                </p>
              </motion.div>
            ) : (
               <div className="w-full p-4 rounded-md bg-surface-200 border border-border space-y-1 min-h-[80px] flex items-center justify-center">
                  <Loader2 className="w-5 h-5 text-text-tertiary animate-spin" />
               </div>
            )}

            <div className="w-full space-y-4">
              <div className="flex items-center justify-between text-sm">
                <span className="text-text-secondary flex items-center gap-1.5"><Users className="w-4 h-4"/> Referrals</span>
                <span className="text-text-primary font-mono">{data?.referrals || 0}</span>
              </div>
              <div className="w-full h-px bg-border" />
              <div className="space-y-3 text-left">
                <p className="text-sm text-text-primary font-medium">Move up the waitlist</p>
                <p className="text-xs text-text-secondary">Share this link to jump ahead in the queue.</p>
                <div className="flex items-center gap-2 mt-2">
                  <div className="flex-1 h-10 px-3 bg-background border border-border rounded-md flex items-center overflow-hidden">
                    <span className="text-xs text-text-tertiary truncate font-mono">
                      {window.location.origin}?ref={data?.code}
                    </span>
                  </div>
                  <Button variant="secondary" className="h-10 px-3 shrink-0" onClick={copyLink}>
                    {copied ? <Check className="w-4 h-4 text-accent" /> : <Copy className="w-4 h-4" />}
                  </Button>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
