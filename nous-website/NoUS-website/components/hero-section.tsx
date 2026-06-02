import { Button } from "@/components/ui/button"
import { Header } from "./header"
import Link from "next/link"

export function HeroSection() {
  return (
    <section className="flex flex-col items-center text-center relative mx-auto overflow-hidden my-0 py-0 px-4 w-full min-h-screen md:px-0">
      {/* Clean gradient background - no busy imagery */}
      <div className="absolute inset-0 z-0">
        <div className="absolute inset-0 bg-gradient-to-b from-background via-background to-primary/5" />
        {/* Subtle radial glow from center */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_hsl(var(--primary)/0.08)_0%,_transparent_70%)]" />
      </div>

      {/* Header */}
      <div className="absolute top-0 left-0 right-0 z-20">
        <Header />
      </div>

      {/* Main content - centered vertically */}
      <div className="relative z-10 flex flex-col items-center justify-center flex-1 max-w-4xl mx-auto pt-24 pb-16">
        {/* Small status badge */}
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded border border-primary/30 bg-primary/5 mb-8">
          <span className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse" />
          <span className="text-primary font-mono text-xs uppercase tracking-[0.15em]">
            The Severance Begins
          </span>
        </div>

        {/* Infinity symbol - the icon of the revolution */}
        <div className="text-primary text-glow text-8xl md:text-9xl lg:text-[180px] font-light leading-none mb-6 select-none">
          ∞
        </div>

        {/* Core message - V for Vendetta style */}
        <h1 className="text-foreground text-3xl md:text-5xl lg:text-6xl font-bold leading-[1.1] tracking-tight uppercase mb-6">
          Remember, Remember
          <br />
          <span className="text-primary text-glow">The Human You Surrendered</span>
        </h1>

        {/* Single line manifesto */}
        <p className="text-muted-foreground text-lg md:text-xl font-normal leading-relaxed max-w-xl mx-auto mb-10">
          Nousloop severs the loop between you and the algorithms that own you.
        </p>

        {/* Single powerful CTA */}
        <Link href="#pricing-section">
          <Button className="bg-primary text-primary-foreground hover:bg-primary-dark px-10 py-4 rounded font-bold text-lg uppercase tracking-wider box-glow ring-1 ring-primary/30 transition-all">
            Sever The Loop
          </Button>
        </Link>

        {/* Scroll indicator */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-muted-foreground/50">
          <span className="text-xs font-mono uppercase tracking-widest">Scroll</span>
          <div className="w-px h-8 bg-gradient-to-b from-muted-foreground/50 to-transparent" />
        </div>
      </div>
    </section>
  )
}
