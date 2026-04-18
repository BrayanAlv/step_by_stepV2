import { Clock } from "lucide-react"

// Color del dot según tipo de evento
const TYPE_COLORS = {
  user:    "bg-[var(--color-green-dark)]",
  routine: "bg-[var(--color-blue-dark)]",
  premium: "bg-[var(--color-yellow)]",
  report:  "bg-[var(--color-red-dark)]",
  content: "bg-[var(--color-blue-dark)]",
}

export default function ActivityList({ items }) {
  return (
    <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="bg-[var(--color-neutral-light)] border-b border-gray-100 px-5 py-3 flex items-center justify-between">
        <h3 className="text-xs font-semibold text-[var(--color-gray-custom)] uppercase tracking-widest">
          Actividad reciente
        </h3>
        <span className="text-xs font-medium text-[var(--color-gray-custom)] bg-[var(--color-neutral-bg)] px-2.5 py-0.5 rounded-full">
          {items.length} eventos
        </span>
      </div>

      {/* Lista */}
      <div className="divide-y divide-gray-100">
        {items.map((item, i) => {
          const dotColor = TYPE_COLORS[item.type] || "bg-gray-400"

          return (
            <div
              key={item.id}
              className="flex items-start gap-3.5 px-5 py-3.5 hover:bg-[var(--color-neutral-bg)] transition-colors duration-150"
            >
              {/* Línea vertical con dot */}
              <div className="flex flex-col items-center">
                <div className={`w-2.5 h-2.5 rounded-full ${dotColor} flex-shrink-0 mt-0.5`} />
                {i !== items.length - 1 && <div className="w-px h-full bg-gray-200 mt-1" />}
              </div>

              {/* Contenido */}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-[var(--color-dark)]">{item.text}</p>
                <div className="flex items-center gap-1.5 mt-1">
                  <Clock size={11} className="text-[var(--color-gray-custom)]" />
                  <span className="text-xs text-[var(--color-gray-custom)]">{item.time}</span>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}