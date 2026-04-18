import { useState } from "react"
import { Save, AlertCircle } from "lucide-react"

export default function RecommendationEditor() {
  const [text, setText] = useState("")
  const [saved, setSaved] = useState(false)
  const [focused, setFocused] = useState(false)

  const handleSave = () => {
    if (!text.trim()) return
    // 🔌 aquí conectarías el backend
    setSaved(true)
    setTimeout(() => setSaved(false), 2500)
  }

  const charCount = text.length
  const isLongEnough = charCount >= 20

  return (
    <div className="bg-[var(--color-blue-light)] rounded-xl p-5 space-y-4">
      {/* Header con icono informativo */}
      <div className="flex items-start gap-3">
        <div className="w-8 h-8 rounded-lg bg-white flex items-center justify-center flex-shrink-0 shadow-sm">
          <AlertCircle size={16} className="text-[var(--color-blue-dark)]" />
        </div>
        <div>
          <label className="block text-sm font-semibold text-[var(--color-dark)]">
            Texto base de recomendaciones
          </label>
          <p className="text-xs text-[var(--color-gray-custom)] mt-0.5">
            Este mensaje se mostrará a los usuarios cuando soliciten recomendaciones personalizadas
          </p>
        </div>
      </div>

      {/* Textarea */}
      <div className="relative">
        <textarea
          rows={5}
          placeholder="Ejemplo: Intenta comenzar con hábitos pequeños y alcanzables. La constancia es más importante que la perfección..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          className={`
            w-full border rounded-xl px-4 py-3 text-sm resize-none
            bg-white text-[var(--color-dark)]
            placeholder-gray-400 outline-none transition-all duration-200
            ${focused
              ? "border-[var(--color-blue-dark)] ring-2 ring-white shadow-sm"
              : "border-white"
            }
          `}
        />
        
        {/* Badge de validación en tiempo real */}
        {text.trim() && (
          <div className={`absolute top-3 right-3 text-xs font-semibold px-2 py-0.5 rounded-full ${
            isLongEnough
              ? "bg-[var(--color-green-light)] text-[var(--color-green-dark)]"
              : "bg-[var(--color-yellow-light)] text-[var(--color-dark)]"
          }`}>
            {isLongEnough ? "✓ Listo" : "Muy corto"}
          </div>
        )}
      </div>

      {/* Footer: contador + botón */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-xs text-[var(--color-gray-custom)]">
            {charCount} caracteres
          </span>
          {!isLongEnough && text.length > 0 && (
            <span className="text-xs text-[var(--color-gray-custom)]">
              (mínimo 20)
            </span>
          )}
        </div>

        <button
          onClick={handleSave}
          disabled={!isLongEnough}
          className={`
            flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold text-white
            transition-all duration-200 active:scale-95
            ${isLongEnough
              ? "bg-[var(--color-blue-dark)] shadow-md hover:brightness-110 cursor-pointer"
              : "bg-gray-300 cursor-not-allowed"
            }
          `}
        >
          <Save size={14} />
          {saved ? "✓ Guardado" : "Guardar"}
        </button>
      </div>

      {/* Hint */}
      <div className="bg-white rounded-lg p-3 border border-[var(--color-blue-dark)]">
        <p className="text-xs text-[var(--color-gray-custom)]">
          <span className="font-semibold text-[var(--color-dark)]">Tip:</span> Escribe un mensaje alentador que motive a los usuarios a crear rutinas realistas y sostenibles en el tiempo.
        </p>
      </div>
    </div>
  )
}