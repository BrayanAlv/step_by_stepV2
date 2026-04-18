import { Trash2, ChevronDown } from "lucide-react"
import { useState } from "react"
import CategoryHabits from "./CategoryHabits"

export default function CategoryList({
  categories,
  onDelete,
  onAddHabit,
  onDeleteHabit,
  colors
}) {
  const [confirmId, setConfirmId] = useState(null)
  const [openId, setOpenId] = useState(null)

  const getColor = (index) => colors[index % colors.length]

  return (
    <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
      <div className="divide-y divide-gray-100">
        {categories.map((cat, i) => {
          const color = getColor(i)
          const isConfirming = confirmId === cat.id
          const isOpen = openId === cat.id

          return (
            <div key={cat.id}>
              <div
                className={`flex items-center justify-between px-5 py-3.5 cursor-pointer ${
                  isConfirming
                    ? "bg-[var(--color-red-light)]"
                    : "hover:bg-[var(--color-neutral-bg)]"
                }`}
                onClick={() =>
                  setOpenId(isOpen ? null : cat.id)
                }
              >
                <div className="flex items-center gap-3">
                  <div className={`w-8 h-8 rounded-xl ${color.bg} flex items-center justify-center`}>
                    <span className="text-sm">{cat.emoji}</span>
                  </div>

                  <span className={`text-xs font-semibold px-3 py-1 rounded-full border ${color.bg} ${color.text} ${color.border}`}>
                    {cat.name}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <ChevronDown
                    size={16}
                    className={`transition-transform ${isOpen ? "rotate-180" : ""}`}
                  />

                  {!isConfirming ? (
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        setConfirmId(cat.id)
                      }}
                    >
                      <Trash2 size={15} />
                    </button>
                  ) : (
                    <>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          onDelete(cat.id)
                          setConfirmId(null)
                        }}
                      >
                        Confirmar
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          setConfirmId(null)
                        }}
                      >
                        Cancelar
                      </button>
                    </>
                  )}
                </div>
              </div>

              {isOpen && (
                <CategoryHabits
                  category={cat}
                  onAddHabit={onAddHabit}
                  onDeleteHabit={onDeleteHabit}
                />
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
