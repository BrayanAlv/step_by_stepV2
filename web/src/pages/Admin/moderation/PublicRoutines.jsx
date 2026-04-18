import { useEffect, useRef, useState } from "react"
import { animate, stagger } from "animejs"
import { Globe, Search, Filter } from "lucide-react"
import RoutineCard from "../../../components/admin/moderation/RoutineCard"
import RoutineDetailModal from "../../../components/admin/moderation/RoutineDetailModal"

export default function PublicRoutines() {
  const [routines, setRoutines] = useState([])
  const [selectedRoutine, setSelectedRoutine] = useState(null)
  const [searchTerm, setSearchTerm] = useState("")

  const headerRef = useRef(null)
  const gridRef = useRef(null)

  useEffect(() => {
    fetchRoutines()

    animate(headerRef.current, {
      translateY: [-20, 0],
      opacity: [0, 1],
      duration: 600,
      easing: "easeOutExpo"
    })
  }, [])

  // 🔥 Evitar horarios repetidos
  const getUniqueHabits = (habitos) => {
    const seen = new Set()

    return habitos.filter(h => {
      if (seen.has(h.tiempo_programado)) return false
      seen.add(h.tiempo_programado)
      return true
    })
  }

  // 🔥 FETCH PRINCIPAL
  const fetchRoutines = async () => {
    try {
      const res = await fetch("https://stepbystep.cv/api/v1/rutinas/?skip=0&limit=100")
      const data = await res.json()

      const publicRoutines = data.filter(r => r.es_publica)

      // 🔥 AQUÍ ESTÁ LO IMPORTANTE (comentarios reales)
      const formatted = await Promise.all(
        publicRoutines.map(async (r) => {
          const uniqueHabits = getUniqueHabits(r.habitos || [])

          let commentsCount = 0

          try {
            const resComments = await fetch(
              `https://stepbystep.cv/api/v1/comunidad/comentarios/${r.id}`
            )
            const commentsData = await resComments.json()
            commentsCount = commentsData.length
          } catch (error) {
            console.error("Error comentarios:", error)
          }

          return {
            id: r.id,
            title: r.nombre,
            author: `Usuario ${r.usuario_id}`,
            description: r.momento_dia,
            likes: r.total_likes,
            comments: commentsCount, // 🔥 YA ES REAL
            shares: 0,
            liked: false,

            habits: uniqueHabits.map(h => ({
              id: h.id,
              text: `${h.tiempo_programado.slice(0, 5)} - ${h.nombre}`
            })),

            raw: r
          }
        })
      )

      setRoutines(formatted)

      setTimeout(() => {
        if (gridRef.current) {
          animate(gridRef.current.children, {
            translateY: [50, 0],
            opacity: [0, 1],
            delay: stagger(100, { start: 200 }),
            duration: 800,
            easing: "easeOutExpo"
          })
        }
      }, 100)

    } catch (error) {
      console.error("Error al cargar rutinas:", error)
    }
  }

  const deleteRoutine = (id) => {
    setRoutines(prev => prev.filter(r => r.id !== id))
    if (selectedRoutine?.id === id) setSelectedRoutine(null)
  }

  return (
    <div className="mx-auto space-y-6">
      {/* Header */}
      <div ref={headerRef} className="flex flex-col md:flex-row justify-between items-end md:items-center gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <div className="w-8 h-8 rounded-xl bg-[var(--color-blue-light)] flex items-center justify-center">
              <Globe size={16} className="text-[var(--color-blue-dark)]" />
            </div>
            <h2 className="text-xl font-bold text-[var(--color-dark)] tracking-tight">
              Explorar Rutinas
            </h2>
          </div>
          <p className="text-xs text-[var(--color-gray-custom)] ml-10">
            Visualiza y modera el contenido generado por la comunidad
          </p>
        </div>

        {/* Buscador */}
        <div className="flex items-center gap-2 w-full md:w-auto">
          <div className="relative flex-1 md:w-64">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar rutinas..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-white border border-gray-200 rounded-xl text-sm outline-none focus:border-[var(--color-blue-dark)]"
            />
          </div>
        </div>
      </div>

      {/* Grid */}
      {routines.filter(r => 
        r.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
        r.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        r.author.toLowerCase().includes(searchTerm.toLowerCase())
      ).length > 0 ? (
        <div ref={gridRef} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
          {routines.filter(r => 
            r.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
            r.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
            r.author.toLowerCase().includes(searchTerm.toLowerCase())
          ).map(routine => (
            <div
              key={routine.id}
              className="h-full cursor-pointer"
              onClick={() => setSelectedRoutine(routine)}
            >
              <RoutineCard
                routine={routine}
                onDelete={() => deleteRoutine(routine.id)}
              />
            </div>
          ))}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-20 text-[var(--color-gray-custom)]">
          <Globe size={48} className="mb-4 text-gray-200" />
          <p>No se encontraron rutinas públicas.</p>
        </div>
      )}

      {/* Modal */}
      {selectedRoutine && (
        <RoutineDetailModal
          routine={selectedRoutine}
          onClose={() => setSelectedRoutine(null)}
        />
      )}
    </div>
  )
}
// import { useEffect, useRef, useState } from "react"
// import { animate, stagger } from "animejs"
// import { Globe, Search, Filter } from "lucide-react"
// import RoutineCard from "../../../components/admin/moderation/RoutineCard"
// import RoutineDetailModal from "../../../components/admin/moderation/RoutineDetailModal"

// export default function PublicRoutines() {
//   const [routines, setRoutines] = useState([])
//   const [selectedRoutine, setSelectedRoutine] = useState(null)

//   const headerRef = useRef(null)
//   const gridRef = useRef(null)

//   useEffect(() => {
//     fetchRoutines()

//     animate(headerRef.current, {
//       translateY: [-20, 0],
//       opacity: [0, 1],
//       duration: 600,
//       easing: "easeOutExpo"
//     })
//   }, [])

//   // 🔥 Función para evitar horarios repetidos
//   const getUniqueHabits = (habitos) => {
//     const seen = new Set()

//     return habitos.filter(h => {
//       if (seen.has(h.tiempo_programado)) return false
//       seen.add(h.tiempo_programado)
//       return true
//     })
//   }

//   const fetchRoutines = async () => {
//     try {
//       const res = await fetch("https://stepbystep.cv/api/v1/rutinas/?skip=0&limit=100")
//       const data = await res.json()

//       // 🔥 Filtrar solo públicas
//       const publicRoutines = data.filter(r => r.es_publica)

//       // 🔥 Adaptar datos + agregar hábitos ya procesados
//       const formatted = publicRoutines.map(r => {
//         const uniqueHabits = getUniqueHabits(r.habitos || [])

//         return {
//           id: r.id,
//           title: r.nombre,
//           author: `Usuario ${r.usuario_id}`,
//           description: r.momento_dia, // este se queda como "mañana"
//           likes: r.total_likes,
//           comments: 0,
//           shares: 0,
//           liked: false,

//           // 👇 NUEVO: hábitos listos para mostrar en lugar del segundo "mañana"
//           habits: uniqueHabits.map(h => ({
//             id: h.id,
//             text: `${h.tiempo_programado.slice(0, 5)} - ${h.nombre}`
//           })),

//           raw: r
//         }
//       })

//       setRoutines(formatted)

//       setTimeout(() => {
//         if (gridRef.current) {
//           animate(gridRef.current.children, {
//             translateY: [50, 0],
//             opacity: [0, 1],
//             delay: stagger(100, { start: 200 }),
//             duration: 800,
//             easing: "easeOutExpo"
//           })
//         }
//       }, 100)

//     } catch (error) {
//       console.error("Error al cargar rutinas:", error)
//     }
//   }

//   const deleteRoutine = (id) => {
//     setRoutines(prev => prev.filter(r => r.id !== id))
//     if (selectedRoutine?.id === id) setSelectedRoutine(null)
//   }

//   return (
//     <div className="mx-auto space-y-6">
//       {/* Header */}
//       <div ref={headerRef} className="flex flex-col md:flex-row justify-between items-end md:items-center gap-4">
//         <div>
//           <div className="flex items-center gap-2 mb-1">
//             <div className="w-8 h-8 rounded-xl bg-[var(--color-blue-light)] flex items-center justify-center">
//               <Globe size={16} className="text-[var(--color-blue-dark)]" />
//             </div>
//             <h2 className="text-xl font-bold text-[var(--color-dark)] tracking-tight">
//               Explorar Rutinas
//             </h2>
//           </div>
//           <p className="text-xs text-[var(--color-gray-custom)] ml-10">
//             Visualiza y modera el contenido generado por la comunidad
//           </p>
//         </div>

//         {/* Buscador */}
//         <div className="flex items-center gap-2 w-full md:w-auto">
//           <div className="relative flex-1 md:w-64">
//             <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
//             <input
//               type="text"
//               placeholder="Buscar rutinas..."
//               className="w-full pl-9 pr-4 py-2 bg-white border border-gray-200 rounded-xl text-sm"
//             />
//           </div>
//           <button className="p-2 bg-white border border-gray-200 rounded-xl">
//             <Filter size={16} />
//           </button>
//         </div>
//       </div>

//       {/* Grid */}
//       {routines.length > 0 ? (
//         <div ref={gridRef} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
//           {routines.map(routine => (
//             <div
//               key={routine.id}
//               className="h-full cursor-pointer"
//               onClick={() => setSelectedRoutine(routine)}
//             >
//               <RoutineCard
//                 routine={routine}
//                 onDelete={() => deleteRoutine(routine.id)}
//               />
//             </div>
//           ))}
//         </div>
//       ) : (
//         <div className="flex flex-col items-center justify-center py-20 text-[var(--color-gray-custom)]">
//           <Globe size={48} className="mb-4 text-gray-200" />
//           <p>No se encontraron rutinas públicas.</p>
//         </div>
//       )}

//       {/* Modal */}
//       {selectedRoutine && (
//         <RoutineDetailModal
//           routine={selectedRoutine}
//           onClose={() => setSelectedRoutine(null)}
//         />
//       )}
//     </div>
//   )
// }
// import { useEffect, useRef, useState } from "react"
// import { animate, stagger } from "animejs"
// import { Globe, Search, Filter } from "lucide-react"
// import RoutineCard from "../../../components/admin/moderation/RoutineCard"
// import RoutineDetailModal from "../../../components/admin/moderation/RoutineDetailModal"

// const MOCK_ROUTINES = [
//   {
//     id: 1,
//     title: "Despertar Energético",
//     author: "Ana García",
//     authorAvatar: null,
//     date: "Hace 2 horas",
//     description: "Una rutina de 15 minutos para activar todo tu cuerpo antes del desayuno. Incluye estiramientos dinámicos y respiración.",
//     tags: ["Mañana", "Flexibilidad", "Rápido"],
//     likes: 124,
//     comments: 45,
//     shares: 12,
//     liked: true
//   },
//   {
//     id: 2,
//     title: "Potencia de Piernas en Casa",
//     author: "Carlos Ruiz",
//     date: "Hace 5 horas",
//     description: "Entrenamiento enfocado en cuádriceps y glúteos sin necesidad de equipo. Perfecto para principiantes.",
//     tags: ["Fuerza", "Piernas", "Casa"],
//     likes: 89,
//     comments: 23,
//     shares: 5,
//     liked: false
//   },
//   {
//     id: 3,
//     title: "Yoga para Dormir Mejor",
//     author: "Sofía M.",
//     date: "Ayer",
//     description: "Secuencia relajante para bajar las revoluciones antes de ir a la cama.",
//     tags: ["Yoga", "Relax", "Noche"],
//     likes: 256,
//     comments: 89,
//     shares: 45,
//     liked: true
//   },
//   {
//     id: 4,
//     title: "Cardio HIIT Explosivo",
//     author: "Miguel Fit",
//     date: "Ayer",
//     description: "Quema calorías con esta rutina de intervalos de alta intensidad. No apta para cardíacos.",
//     tags: ["Cardio", "HIIT", "Avanzado"],
//     likes: 42,
//     comments: 8,
//     shares: 2,
//     liked: false
//   },
//   {
//     id: 5,
//     title: "Estiramiento de Oficina",
//     author: "Laura Tech",
//     date: "Hace 2 días",
//     description: "Ejercicios simples para hacer en tu silla y evitar dolores de espalda por el trabajo.",
//     tags: ["Salud", "Oficina", "Postura"],
//     likes: 312,
//     comments: 15,
//     shares: 89,
//     liked: true
//   }
// ]

// export default function PublicRoutines() {
//   const [routines, setRoutines] = useState(MOCK_ROUTINES)
//   const [selectedRoutine, setSelectedRoutine] = useState(null)

//   const headerRef = useRef(null)
//   const gridRef = useRef(null)

//   useEffect(() => {
//     // Animación Header
//     animate(headerRef.current, {
//       translateY: [-20, 0],
//       opacity: [0, 1],
//       duration: 600,
//       easing: "easeOutExpo"
//     })

//     // Animación Grid (Staggered)
//     if (gridRef.current) {
//       animate(gridRef.current.children, {
//         translateY: [50, 0],
//         opacity: [0, 1],
//         delay: stagger(100, { start: 200 }),
//         duration: 800,
//         easing: "easeOutExpo"
//       })
//     }
//   }, [])

//   const deleteRoutine = (id) => {
//     // Simulamos eliminación visual
//     setRoutines(prev => prev.filter(r => r.id !== id))
//     if (selectedRoutine?.id === id) setSelectedRoutine(null)
//   }

//   return (
//     <div className="mx-auto space-y-6">
//       {/* Header Sección */}
//       <div ref={headerRef} className="flex flex-col md:flex-row justify-between items-end md:items-center gap-4">
//         <div>
//           <div className="flex items-center gap-2 mb-1">
//             <div className="w-8 h-8 rounded-xl bg-[var(--color-blue-light)] flex items-center justify-center">
//               <Globe size={16} className="text-[var(--color-blue-dark)]" />
//             </div>
//             <h2 className="text-xl font-bold text-[var(--color-dark)] tracking-tight">
//               Explorar Rutinas
//             </h2>
//           </div>
//           <p className="text-xs text-[var(--color-gray-custom)] ml-10">
//             Visualiza y modera el contenido generado por la comunidad
//           </p>
//         </div>

//         {/* Barra de Herramientas (Buscador + Filtro) */}
//         <div className="flex items-center gap-2 w-full md:w-auto">
//           <div className="relative flex-1 md:w-64">
//             <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
//             <input
//               type="text"
//               placeholder="Buscar rutinas..."
//               className="w-full pl-9 pr-4 py-2 bg-white border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-[var(--color-blue-dark)] focus:ring-2 focus:ring-[var(--color-blue-light)] transition-all"
//             />
//           </div>
//           <button className="p-2 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 text-[var(--color-gray-custom)] transition-colors">
//             <Filter size={16} />
//           </button>
//         </div>
//       </div>

//       {/* Grid de Rutinas */}
//       {routines.length > 0 ? (
//         <div ref={gridRef} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
//           {routines.map(routine => (
//             <div
//               key={routine.id}
//               className="h-full cursor-pointer"
//               onClick={() => setSelectedRoutine(routine)}
//             >
//               <RoutineCard
//                 routine={routine}
//                 onDelete={() => deleteRoutine(routine.id)}
//               />
//             </div>
//           ))}
//         </div>
//       ) : (
//         <div className="flex flex-col items-center justify-center py-20 text-[var(--color-gray-custom)] opacity-0 animate-fade-in">
//           <Globe size={48} className="mb-4 text-gray-200" />
//           <p>No se encontraron rutinas públicas.</p>
//         </div>
//       )}

//       {/* Modal de Detalles */}
//       {selectedRoutine && (
//         <RoutineDetailModal
//           routine={selectedRoutine}
//           onClose={() => setSelectedRoutine(null)}
//         />
//       )}
//     </div>
//   )
// }
