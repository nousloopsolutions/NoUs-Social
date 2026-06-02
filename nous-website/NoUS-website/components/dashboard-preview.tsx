import Image from "next/image" // Import the Image component

export function DashboardPreview() {
  return (
    <div className="w-[calc(100vw-32px)] md:w-[1160px]">
      <div className="relative bg-primary/20 rounded-2xl p-2 shadow-2xl ring-1 ring-primary/30 box-glow h-[280px] md:h-[450px] lg:h-[600px] overflow-hidden">
        <Image
          src="/images/lets-sever-humans.jpg"
          alt="Hooded figures on a neon-lit dystopian highway beneath a glowing 'Let's Sever Humans' infinity sign"
          fill
          sizes="(max-width: 768px) calc(100vw - 32px), 1160px"
          className="object-cover rounded-lg"
          priority
        />
      </div>
    </div>
  )
}
