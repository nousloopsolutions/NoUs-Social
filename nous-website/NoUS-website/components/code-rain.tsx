"use client"

import { useEffect, useRef } from "react"

export function CodeRain() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    // Characters: katakana + latin + digits for a cyberpunk feel
    const chars =
      "アカサタナハマヤラワabcdefghijklmnopqrstuvwxyz0123456789∞{}[]()<>=+*#$%&".split("")

    let width = 0
    let height = 0
    let columns = 0
    let drops: number[] = []
    const fontSize = 16

    const setup = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2)
      width = window.innerWidth
      height = window.innerHeight
      canvas.width = width * dpr
      canvas.height = height * dpr
      canvas.style.width = `${width}px`
      canvas.style.height = `${height}px`
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
      columns = Math.floor(width / fontSize)
      // Start drops at random negative offsets so the rain begins staggered
      drops = Array.from({ length: columns }, () => Math.floor((Math.random() * -height) / fontSize))
    }

    setup()

    let animationFrame: number
    let lastTime = 0
    const interval = 55 // ms between frames — controls fall speed

    const draw = (time: number) => {
      animationFrame = requestAnimationFrame(draw)
      if (time - lastTime < interval) return
      lastTime = time

      // Translucent fade for the trailing effect (matches near-black bg)
      ctx.fillStyle = "rgba(7, 12, 13, 0.08)"
      ctx.fillRect(0, 0, width, height)

      ctx.font = `${fontSize}px "Roboto Mono", monospace`

      for (let i = 0; i < drops.length; i++) {
        const char = chars[Math.floor(Math.random() * chars.length)]
        const x = i * fontSize
        const y = drops[i] * fontSize

        // Lead character glows bright/white, trail is teal
        const isHead = Math.random() > 0.975
        if (isHead) {
          ctx.fillStyle = "rgba(236, 244, 244, 0.95)"
        } else {
          ctx.fillStyle = "rgba(40, 239, 208, 0.55)"
        }
        ctx.fillText(char, x, y)

        // Reset drop to top once it passes bottom, with randomness
        if (y > height && Math.random() > 0.975) {
          drops[i] = 0
        }
        drops[i]++
      }
    }

    animationFrame = requestAnimationFrame(draw)

    const handleResize = () => setup()
    window.addEventListener("resize", handleResize)

    return () => {
      cancelAnimationFrame(animationFrame)
      window.removeEventListener("resize", handleResize)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      aria-hidden="true"
      className="pointer-events-none fixed inset-0 z-0 h-full w-full opacity-25"
    />
  )
}
