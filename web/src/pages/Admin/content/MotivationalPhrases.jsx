import { useEffect, useRef, useState } from "react"
import { animate, stagger } from "animejs"
import { MessageCircle, Trash2 } from "lucide-react"
import PhraseForm from "../../../components/admin/content/PhraseForm"

export default function MotivationalPhrases() {
  const [phrases, setPhrases] = useState([])
  const [confirmId, setConfirmId] = useState(null)

  const headerRef = useRef(null)
  const badgesRef = useRef(null)
  const listRef = useRef(null)

  useEffect(() => {

    // 🔥 Animaciones
    animate(headerRef.current, {
      translateY: [-20, 0],
      opacity: [0, 1],
      duration: 500,
      easing: "ease-out",
    })

    animate(badgesRef.current?.children, {
      scale: [0.8, 1],
      opacity: [0, 1],
      delay: stagger(120),
    })

    // Fetch frases desde API
    const fetchPhrases = async () => {
      try {
        const response = await fetch("https://stepbystep.cv/api/v1/frases/?skip=0&limit=100")
        const data = await response.json()

        const formatted = data.map(p => ({
          id: p.id,
          text: p.texto,
          author: p.autor,
          category: p.categoria,
          active: true // 👈 no viene del backend
        }))

        setPhrases(formatted)

        // animación lista
        setTimeout(() => {
          animate(listRef.current?.children, {
            translateY: [20, 0],
            opacity: [0, 1],
            delay: stagger(80),
          })
        }, 100)

      } catch (error) {
        console.error("Error cargando frases:", error)
      }
    }

    fetchPhrases()

  }, [])

  const addPhrase = (newPhrase) => {
    setPhrases((prev) => [...prev, newPhrase])
  }

  const togglePhrase = (id) => {
    setPhrases((prev) =>
      prev.map((p) =>
        p.id === id ? { ...p, active: !p.active } : p
      )
    )
  }

  const deletePhrase = async (id) => {
    try {
      const response = await fetch(`https://stepbystep.cv/api/v1/frases/${id}`, {
        method: 'DELETE',
      })
      if (response.ok) {
        setPhrases((prev) => prev.filter((p) => p.id !== id))
        setConfirmId(null)
      } else {
        console.error("Error eliminando la frase")
      }
    } catch (error) {
      console.error("Error:", error)
    }
  }

  const activeCount = phrases.filter((p) => p.active).length

  return (
    <div className="mx-auto space-y-5">

      {/* Header */}
      <div ref={headerRef} className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-[var(--color-blue-light)] flex items-center justify-center">
              <MessageCircle size={16} className="text-[var(--color-blue-dark)]" />
            </div>
            <h2 className="text-xl font-bold text-[var(--color-dark)]">
              Frases motivacionales
            </h2>
          </div>
          <p className="text-xs text-[var(--color-gray-custom)] mt-1 ml-10">
            Gestiona las frases que verán los usuarios durante sus rutinas
          </p>
        </div>

        {/* Badges */}
        <div ref={badgesRef} className="flex items-center gap-2">
          <span className="text-xs font-semibold text-[var(--color-green-dark)] bg-[var(--color-green-light)] px-3 py-1 rounded-full">
            {activeCount} activas
          </span>
          <span className="text-xs font-semibold text-[var(--color-gray-custom)] bg-[var(--color-neutral-bg)] px-3 py-1 rounded-full">
            {phrases.length} total
          </span>
        </div>
      </div>

      {/* Form */}
      <PhraseForm onAdd={addPhrase} />

      {/* Lista */}
      <div
        ref={listRef}
        className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden"
      >
        <div className="bg-[var(--color-green-light)] border-b border-[var(--color-green-dark)] px-5 py-3 flex items-center justify-between">
          <h3 className="text-xs font-semibold text-[var(--color-green-dark)] uppercase tracking-widest">
            Frases actuales
          </h3>
          <span className="text-xs font-semibold text-[var(--color-green-dark)] bg-white px-2.5 py-0.5 rounded-full">
            {phrases.length} frases
          </span>
        </div>

        {phrases.length === 0 ? (
          <div className="py-10 flex flex-col items-center gap-2">
            <span className="text-2xl">💬</span>
            <p className="text-sm text-[var(--color-gray-custom)]">
              No hay frases aún
            </p>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {phrases.map((phrase) => {
              const isConfirming = confirmId === phrase.id

              return (
                <div
                  key={phrase.id}
                  className={`px-5 py-4 ${
                    isConfirming
                      ? "bg-[var(--color-red-light)]"
                      : "hover:bg-[var(--color-neutral-bg)]"
                  }`}
                >
                  {/* Texto */}
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-start gap-3 flex-1">
                      <span
                        className={`text-lg font-bold ${
                          phrase.active
                            ? "text-[var(--color-green-dark)]"
                            : "text-gray-300"
                        }`}
                      >
                        ❝
                      </span>

                      <div>
                        <p className="text-sm">{phrase.text}</p>
                        <p className="text-xs text-gray-400 mt-1">
                          — {phrase.author} · {phrase.category}
                        </p>
                      </div>
                    </div>

                    {/* Estado */}
                    <span
                      className={`text-xs px-2 py-1 rounded-full ${
                        phrase.active
                          ? "bg-green-100 text-green-700"
                          : "bg-gray-100 text-gray-400"
                      }`}
                    >
                      {phrase.active ? "Activa" : "Inactiva"}
                    </span>
                  </div>

                  {/* Acciones */}
                  <div className="flex justify-end gap-2 mt-3">
                    {!isConfirming ? (
                      <>
                        <button
                          onClick={() => togglePhrase(phrase.id)}
                          className={`w-10 h-5 rounded-full ${
                            phrase.active ? "bg-green-600" : "bg-gray-300"
                          }`}
                        />

                        <button
                          onClick={() => setConfirmId(phrase.id)}
                          className="text-gray-400 hover:text-red-500"
                        >
                          <Trash2 size={14} />
                        </button>
                      </>
                    ) : (
                      <>
                        <button
                          onClick={() => deletePhrase(phrase.id)}
                          className="text-xs text-white bg-red-600 px-3 py-1 rounded"
                        >
                          Confirmar
                        </button>
                        <button
                          onClick={() => setConfirmId(null)}
                          className="text-xs text-gray-500"
                        >
                          Cancelar
                        </button>
                      </>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
// import { useEffect, useRef, useState } from "react"
// import { animate, stagger } from "animejs"
// import { MessageCircle, Trash2 } from "lucide-react"
// import PhraseForm from "../../../components/admin/content/PhraseForm"

// const INITIAL_PHRASES = [
//   { id: 1, text: "Un paso a la vez también es progreso", active: true },
//   { id: 3, text: "Tu constancia vale más que la perfección", active: false },
// ]

// export default function MotivationalPhrases() {
//   const [phrases, setPhrases] = useState(INITIAL_PHRASES)
//   const [confirmId, setConfirmId] = useState(null)
//   const [toast] = useState({ show: false, text: "", type: "success" })
//   const headerRef = useRef(null)
//   const badgesRef = useRef(null)
//   const listRef = useRef(null)
//   const toastRef = useRef(null)

//   useEffect(() => {

//     animate(headerRef.current, {
//       translateY: [-20, 0],
//       opacity: [0, 1],
//       duration: 500,
//       easing: "ease-out",
//     })

//     animate(badgesRef.current?.children, {
//       scale: [0.8, 1],
//       opacity: [0, 1],
//       delay: stagger(120),
//     })

//     animate(listRef.current?.children, {
//       translateY: [20, 0],
//       opacity: [0, 1],
//       delay: stagger(80),
//     })

//   }, [])


//   const showToast = (text, type = "success") => {
//     setTimeout(() => {
//       animate(toastRef.current, {
//         scale: [0.8, 1],
//         opacity: [0, 1],
//         duration: 300,
//         easing: "ease-out",
//       })
//     }, 50)
//   }

//   const addPhrase = (text) => {
//     setPhrases((prev) => [...prev, { id: Date.now(), text, active: true }])
//     showToast("Frase añadida")
//   }

//   const togglePhrase = (id) => {
//     setPhrases((prev) =>
//       prev.map((p) => (p.id === id ? { ...p, active: !p.active } : p))
//     )
//   }

//   const deletePhrase = (id) => {
//     setPhrases((prev) => prev.filter((p) => p.id !== id))
//     setConfirmId(null)
//     showToast("Frase eliminada", "error")
//   }

//   const activeCount = phrases.filter((p) => p.active).length

//   return (
//     <div className="mx-auto space-y-5">
//       {/* Toast */}
//       <div ref={toastRef}
//         className={`
//           fixed top-5 right-5 z-50 flex items-center gap-2
//           text-xs font-semibold px-5 py-2.5 rounded-lg shadow-lg text-white
//           transition-all duration-300 ease-out
//           ${toast.show ? "translate-y-0 opacity-100" : "-translate-y-16 opacity-0"}
//           ${toast.type === "success" ? "bg-[var(--color-green-dark)]" : "bg-[var(--color-red-dark)]"}
//         `}
//       >
//         <span>{toast.type === "success" ? "✓" : "✕"}</span>
//         {toast.text}
//       </div>

//       {/* Header */}
//       <div ref={headerRef} className="flex items-center justify-between">
//         <div>
//           <div className="flex items-center gap-2">
//             <div className="w-8 h-8 rounded-xl bg-[var(--color-blue-light)] flex items-center justify-center">
//               <MessageCircle size={16} className="text-[var(--color-blue-dark)]" />
//             </div>
//             <h2 className="text-xl font-bold text-[var(--color-dark)] tracking-tight">
//               Frases motivacionales
//             </h2>
//           </div>
//           <p className="text-xs text-[var(--color-gray-custom)] mt-1 ml-10">
//             Gestiona las frases que verán los usuarios durante sus rutinas
//           </p>
//         </div>
//         {/* Badges */}
//         <div ref={badgesRef} className="flex items-center gap-2">
//           <span className="text-xs font-semibold text-[var(--color-green-dark)] bg-[var(--color-green-light)] px-3 py-1 rounded-full">
//             {activeCount} activas
//           </span>
//           <span className="text-xs font-semibold text-[var(--color-gray-custom)] bg-[var(--color-neutral-bg)] px-3 py-1 rounded-full">
//             {phrases.length} total
//           </span>
//         </div>
//       </div>

//       {/* Form */}
//       <PhraseForm onAdd={addPhrase} />

//       {/* Lista de frases */}
//       <div ref={listRef} className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
//         <div className="bg-[var(--color-green-light)] border-b border-[var(--color-green-dark)] px-5 py-3 flex items-center justify-between">
//           <h3 className="text-xs font-semibold text-[var(--color-green-dark)] uppercase tracking-widest">
//             Frases actuales
//           </h3>
//           <span className="text-xs font-semibold text-[var(--color-green-dark)] bg-white px-2.5 py-0.5 rounded-full shadow-sm">
//             {phrases.length} frases
//           </span>
//         </div>

//         {phrases.length === 0 ? (
//           <div className="py-10 flex flex-col items-center gap-2">
//             <span className="text-2xl">💬</span>
//             <p className="text-sm text-[var(--color-gray-custom)]">No hay frases aún</p>
//             <p className="text-xs text-[var(--color-gray-custom)]">Crea una desde el formulario de arriba</p>
//           </div>
//         ) : (
//           <div className="divide-y divide-gray-100">
//             {phrases.map((phrase) => {
//               const isConfirming = confirmId === phrase.id

//               return (
//                 <div
//                   key={phrase.id}
//                   className={`px-5 py-4 transition-colors duration-200 ${isConfirming ? "bg-[var(--color-red-light)]" : "hover:bg-[var(--color-neutral-bg)]"
//                     }`}
//                 >
//                   {/* Texto + badge estado */}
//                   <div className="flex items-start justify-between gap-3">
//                     <div className="flex items-start gap-3 flex-1 min-w-0">
//                       {/* Comillas decorativas */}
//                       <span className={`text-lg font-bold leading-none mt-0.5 flex-shrink-0 ${phrase.active ? "text-[var(--color-green-dark)]" : "text-gray-300"
//                         }`}>
//                         ❝
//                       </span>
//                       <p className={`text-sm leading-relaxed ${phrase.active ? "text-[var(--color-dark)]" : "text-[var(--color-gray-custom)] italic"
//                         }`}>
//                         {phrase.text}
//                       </p>
//                     </div>

//                     {/* Badge activa/inactiva */}
//                     <span
//                       className={`flex-shrink-0 text-xs font-semibold px-2.5 py-0.5 rounded-full ${phrase.active
//                         ? "bg-[var(--color-green-light)] text-[var(--color-green-dark)]"
//                         : "bg-[var(--color-neutral-bg)] text-[var(--color-gray-custom)]"
//                         }`}
//                     >
//                       {phrase.active ? "Activa" : "Inactiva"}
//                     </span>
//                   </div>

//                   {/* Acciones */}
//                   <div className="flex items-center justify-end gap-2 mt-3">
//                     {!isConfirming ? (
//                       <>
//                         {/* Toggle activa/inactiva */}
//                         <button
//                           onClick={() => togglePhrase(phrase.id)}
//                           className={`relative w-10 h-5 rounded-full transition-colors duration-300 ease-out focus:outline-none ${phrase.active ? "bg-[var(--color-green-dark)]" : "bg-gray-300"
//                             }`}
//                         >
//                           <span
//                             className={`absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform duration-300 ease-out ${phrase.active ? "translate-x-5" : "translate-x-0"
//                               }`}
//                           />
//                         </button>

//                         {/* Eliminar */}
//                         <button
//                           onClick={() => setConfirmId(phrase.id)}
//                           className="w-7 h-7 rounded-lg flex items-center justify-center text-[var(--color-gray-custom)] hover:bg-[var(--color-red-light)] hover:text-[var(--color-red-dark)] transition-all duration-200"
//                         >
//                           <Trash2 size={14} />
//                         </button>
//                       </>
//                     ) : (
//                       <>
//                         <button
//                           onClick={() => deletePhrase(phrase.id)}
//                           className="text-xs font-semibold text-white bg-[var(--color-red-dark)] px-3 py-1 rounded-lg hover:brightness-110 active:scale-95 transition-all duration-200"
//                         >
//                           Confirmar
//                         </button>
//                         <button
//                           onClick={() => setConfirmId(null)}
//                           className="text-xs font-semibold text-[var(--color-gray-custom)] bg-[var(--color-neutral-bg)] px-3 py-1 rounded-lg hover:bg-gray-200 transition-all duration-200"
//                         >
//                           Cancelar
//                         </button>
//                       </>
//                     )}
//                   </div>
//                 </div>
//               )
//             })}
//           </div>
//         )}
//       </div>
//     </div>
//   )
// }