import { useState, useEffect } from "react"
import { Plus } from "lucide-react"

export default function PhraseForm({ onAdd }) {
  const [text, setText] = useState("")
  const [author, setAuthor] = useState("")
  const [category, setCategory] = useState("")
  const [categoriesList, setCategoriesList] = useState([])
  const [focused, setFocused] = useState(false)
  const [loading, setLoading] = useState(false)

  // Cargar categorías disponibles desde DB
  useEffect(() => {
    fetch("https://stepbystep.cv/api/v1/rutinas/categorias")
      .then(res => res.json())
      .then(data => setCategoriesList(data || []))
      .catch(err => console.error("Error trayendo categorías:", err))
  }, [])

  const handleSubmit = async () => {
    const trimmed = text.trim()
    if (!trimmed || loading) return

    setLoading(true)

    try {
      const response = await fetch("https://stepbystep.cv/api/v1/frases/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          texto: trimmed,
          autor: author || "Anónimo",
          categoria: category || "General"
        })
      })

      const data = await response.json()

      if (!response.ok) {
        console.warn("Puede que sí se haya guardado 👀", data)
      }

      // 👉 actualizar UI
      onAdd({
        id: data?.id || Date.now(),
        text: data?.texto || trimmed,
        author: data?.autor || author,
        category: data?.categoria || category,
        active: true
      })

      // limpiar campos
      setText("")
      setAuthor("")
      setCategory("")

    } catch (error) {
      console.error("Error al crear frase:", error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
      
      <div className="bg-[var(--color-blue-light)] border-b border-[var(--color-blue-dark)] px-5 py-3">
        <h3 className="text-xs font-semibold text-[var(--color-blue-dark)] uppercase tracking-widest">
          Nueva frase
        </h3>
      </div>

      <div className="p-5 space-y-3">

        {/* TEXTAREA */}
        <div className="relative">
          <span className="absolute left-3 top-2.5 text-lg font-bold text-[var(--color-green-dark)]">❝</span>
          <textarea
            rows={2}
            placeholder="Escribe una frase motivacional..."
            value={text}
            onChange={(e) => setText(e.target.value)}
            onFocus={() => setFocused(true)}
            onBlur={() => setFocused(false)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault()
                handleSubmit()
              }
            }}
            className={`
              w-full border rounded-xl pl-8 pr-4 py-2.5 text-sm resize-none
              ${focused
                ? "border-[var(--color-green-dark)] ring-2 ring-[var(--color-green-light)] bg-white"
                : "border-gray-200 bg-[var(--color-neutral-light)]"
              }
            `}
          />
        </div>

        {/* AUTOR */}
        <input
          type="text"
          placeholder="Autor (opcional)"
          value={author}
          onChange={(e) => setAuthor(e.target.value)}
          className="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm"
        />

        {/* CATEGORÍA SELECT */}
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className={`w-full border border-gray-200 rounded-xl px-3 py-2 text-sm bg-white focus:outline-none focus:border-[var(--color-green-dark)] transition-colors ${category === "" ? "text-gray-400" : "text-black"}`}
        >
          <option value="" disabled>Selecciona una categoría (opcional)</option>
          <option value="General">General (Por defecto)</option>
          {categoriesList.map(cat => (
            <option key={cat.id} value={cat.nombre}>
              {cat.nombre}
            </option>
          ))}
        </select>

        {/* FOOTER */}
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-400">
            {text.length} caracteres
          </span>

          <button
            onClick={handleSubmit}
            disabled={!text.trim() || loading}
            className={`
              flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold text-white
              ${text.trim() && !loading
                ? "bg-[var(--color-green-dark)] hover:brightness-110"
                : "bg-gray-300 cursor-not-allowed"
              }
            `}
          >
            <Plus size={14} />
            {loading ? "Guardando..." : "Añadir frase"}
          </button>
        </div>

        <p className="text-xs text-gray-400">
          Presiona Enter para añadir rápido
        </p>
      </div>
    </div>
  )
}

// import { useState } from "react"
// import { Plus } from "lucide-react"

// export default function PhraseForm({ onAdd }) {
//   const [text, setText] = useState("")
//   const [focused, setFocused] = useState(false)

//   const handleSubmit = () => {
//     const trimmed = text.trim()
//     if (!trimmed) return
//     onAdd(trimmed)
//     setText("")
//   }

//   return (
//     <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
//       <div className="bg-[var(--color-blue-light)] border-b border-[var(--color-blue-dark)] px-5 py-3">
//         <h3 className="text-xs font-semibold text-[var(--color-blue-dark)] uppercase tracking-widest">
//           Nueva frase
//         </h3>
//       </div>

//       <div className="p-5 space-y-3">
//         {/* Textarea con comillas decorativas */}
//         <div className="relative">
//           <span className="absolute left-3 top-2.5 text-lg font-bold text-[var(--color-green-dark)] leading-none">❝</span>
//           <textarea
//             rows={2}
//             placeholder="Escribe una frase motivacional..."
//             value={text}
//             onChange={(e) => setText(e.target.value)}
//             onFocus={() => setFocused(true)}
//             onBlur={() => setFocused(false)}
//             onKeyDown={(e) => {
//               if (e.key === "Enter" && !e.shiftKey) {
//                 e.preventDefault()
//                 handleSubmit()
//               }
//             }}
//             className={`
//               w-full border rounded-xl pl-8 pr-4 py-2.5 text-sm resize-none
//               bg-[var(--color-neutral-light)] text-[var(--color-dark)]
//               placeholder-gray-400 outline-none transition-all duration-200
//               ${focused
//                 ? "border-[var(--color-green-dark)] ring-2 ring-[var(--color-green-light)] bg-white"
//                 : "border-gray-200"
//               }
//             `}
//           />
//         </div>

//         {/* Footer: contador + botón */}
//         <div className="flex items-center justify-between">
//           <span className="text-xs text-[var(--color-gray-custom)]">
//             {text.length} caracteres
//           </span>
//           <button
//             onClick={handleSubmit}
//             disabled={!text.trim()}
//             className={`
//               flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold text-white
//               transition-all duration-200 active:scale-95
//               ${text.trim()
//                 ? "bg-[var(--color-green-dark)] shadow-md hover:brightness-110 cursor-pointer"
//                 : "bg-gray-300 cursor-not-allowed"
//               }
//             `}
//           >
//             <Plus size={14} />
//             Añadir frase
//           </button>
//         </div>

//         {/* Hint */}
//         <p className="text-xs text-[var(--color-gray-custom)]">
//           Presiona <kbd className="bg-[var(--color-neutral-bg)] border border-gray-200 rounded px-1.5 py-0.5 text-[var(--color-dark)] font-semibold text-xs">Enter</kbd> para añadir rápido
//         </p>
//       </div>
//     </div>
//   )
// }