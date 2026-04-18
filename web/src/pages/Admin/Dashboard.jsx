import { useEffect, useRef, useState } from "react"
import { animate, stagger } from "animejs"
import { LayoutDashboard, Users, ClipboardList, Globe, Gem } from "lucide-react"

import StatCard from "../../components/admin/dashboard/StatCard"
import ActivityList from "../../components/admin/dashboard/ActivityList"
import StatDetailsModal from "../../components/admin/dashboard/StatDetailsModal"

// ─── CONFIG ───────────────────────────────────────────────
const STATS = [
  {
    key: "users",
    title: "Usuarios totales",
    value: 0,
    change: 12,
    positive: true,
    bg: "bg-[var(--color-green-light)]",
    headerBg: "bg-[var(--color-green-dark)]",
    icon: Users,
  },
  {
    key: "routines",
    title: "Rutinas creadas",
    value: 0,
    change: 8,
    positive: true,
    bg: "bg-[var(--color-blue-light)]",
    headerBg: "bg-[var(--color-blue-dark)]",
    icon: ClipboardList,
  },
  {
    key: "publicRoutines",
    title: "Rutinas públicas",
    value: 0,
    change: 3,
    positive: false,
    bg: "bg-[var(--color-yellow-light)]",
    headerBg: "bg-[var(--color-yellow)]",
    icon: Globe,
  },
  {
    key: "premiumUsers",
    title: "Usuarios Premium",
    value: 0,
    change: 21,
    positive: true,
    bg: "bg-[var(--color-red-light)]",
    headerBg: "bg-[var(--color-red-dark)]",
    icon: Gem,
  },
]

// ─── ACTIVIDAD ───────────────────────────────────────────
// Los datos de actividad ahora se calculan dinámicamente desde la API.

export default function Dashboard() {

  const [stats, setStats] = useState(STATS)
  const [activity, setActivity] = useState([])
  const [selectedStat, setSelectedStat] = useState(null)
  const [loading, setLoading] = useState(true)

  const headerRef = useRef(null)
  const statsRef = useRef(null)
  const activityRef = useRef(null)

  // ─── FETCH DATA ─────────────────────────────────────────
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)

        // Ejecutar todo en paralelo 🚀
        const [
          usersRes,
          premiumRes,
          routinesRes
        ] = await Promise.all([
          fetch("https://stepbystep.cv/api/v1/usuarios/freemium/all?skip=0&limit=10"),
          fetch("https://stepbystep.cv/api/v1/usuarios/premium/all"),
          fetch("https://stepbystep.cv/api/v1/rutinas/?skip=0&limit=100")
        ])

        // Parsear respuestas
        let usersData = []
        let premiumData = []
        let routinesData = []

        try { usersData = await usersRes.json() } catch (e) { }
        try { premiumData = await premiumRes.json() } catch (e) { }
        try { routinesData = await routinesRes.json() } catch (e) { }

        const usersArray = usersData.data || usersData || []
        const premiumArray = premiumData.data || premiumData || []
        const routinesArray = routinesData.data || routinesData || []

        // ─── TOTALES ───
        const totals = {
          users: usersArray.length,
          routines: routinesArray.length,
          publicRoutines: routinesArray.filter(r => r.es_publica === true).length,
          premiumUsers: premiumArray.length
        }

        // ─── ACTUALIZAR STATS ───
        const updatedStats = STATS.map(stat => ({
          ...stat,
          value: totals[stat.key] || 0
        }))

        setStats(updatedStats)

        // ─── ACTIVIDAD RECIENTE ───
        const recentActivity = [...routinesArray]
          .sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0))
          .slice(0, 5)
          .map((r, index) => {
            const timeDiff = Math.floor((new Date() - new Date(r.created_at || 0)) / 60000);
            let timeStr = "";
            if (timeDiff < 60) timeStr = `Hace ${Math.max(1, timeDiff)} min`;
            else if (timeDiff < 1440) timeStr = `Hace ${Math.floor(timeDiff/60)} h`;
            else timeStr = `Hace ${Math.floor(timeDiff/1440)} d`;

            return {
              id: r.id || index,
              text: r.es_publica ? `Rutina pública publicada: ${r.nombre}` : `Nueva rutina creada: ${r.nombre}`,
              time: timeStr,
              type: r.es_publica ? "globe" : "routine" 
            };
          });

        setActivity(recentActivity.length > 0 ? recentActivity : [{ id: 0, text: "No hay actividad reciente", time: "", type: "info" }]);

      } catch (error) {
        console.error("Error cargando dashboard:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  // ─── ANIMACIONES ────────────────────────────────────────
  useEffect(() => {
    if (loading) return

    animate(headerRef.current, {
      translateY: [-20, 0],
      opacity: [0, 1],
      duration: 600,
      easing: "ease-out",
    })

    animate(statsRef.current?.children, {
      translateY: [40, 0],
      opacity: [0, 1],
      duration: 800,
      easing: "ease-out",
      delay: stagger(120),
    })

    animate(activityRef.current, {
      translateY: [30, 0],
      opacity: [0, 1],
      duration: 700,
      easing: "ease-out",
      delay: 400,
    })

  }, [loading])

  // ─── LOADING ───────────────────────────────────────────
  if (loading) {
    return (
      <div className="min-h-screen bg-[var(--color-neutral-bg)] flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-[var(--color-green-dark)] border-t-transparent rounded-full animate-spin" />
          <p className="text-sm text-[var(--color-gray-custom)]">
            Cargando dashboard...
          </p>
        </div>
      </div>
    )
  }

  // ─── UI ────────────────────────────────────────────────
  return (
    <div className="max-w-6xl mx-auto space-y-6">

      {/* Header */}
      <div ref={headerRef} className="flex items-center gap-2">
        <div className="w-8 h-8 rounded-xl bg-[var(--color-yellow-light)] flex items-center justify-center">
          <LayoutDashboard size={18} className="text-[var(--color-yellow-dark)]" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-[var(--color-dark)] tracking-tight">
            Dashboard
          </h2>
          <p className="text-xs text-[var(--color-gray-custom)] mt-1">
            Resumen general de la plataforma
          </p>
        </div>
      </div>

      {/* Stats */}
      <div
        ref={statsRef}
        className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4"
      >
        {stats.map(({ key, ...stat }) => (
          <StatCard
            key={key}
            {...stat}
            onClick={() => setSelectedStat({ type: key, title: stat.title })}
          />
        ))}
      </div>

      {/* Actividad */}
      <div ref={activityRef}>
        <ActivityList items={activity} />
      </div>

      {/* Modal */}
      {selectedStat && (
        <StatDetailsModal
          type={selectedStat.type}
          title={selectedStat.title}
          onClose={() => setSelectedStat(null)}
        />
      )}

    </div>
  )
}

// import { useEffect, useRef, useState } from "react"
// import { animate, stagger } from "animejs"
// import { LayoutDashboard } from "lucide-react"
// import StatCard from "../../components/admin/dashboard/StatCard"
// import ActivityList from "../../components/admin/dashboard/ActivityList"
// import StatDetailsModal from "../../components/admin/dashboard/StatDetailsModal"

// // ─── Mock data ───────────────────────────────────────────────
// import { Users, ClipboardList, Globe, Gem } from "lucide-react"

// // ─── Mock data ───────────────────────────────────────────────
// const STATS = [
//   {
//     key: "users",
//     title: "Usuarios totales",
//     value: 124,
//     change: 12,
//     positive: true,
//     bg: "bg-[var(--color-green-light)]",
//     headerBg: "bg-[var(--color-green-dark)]",
//     icon: Users,
//     iconColor: "text-[var(--color-green-dark)]",
//   },
//   {
//     key: "routines",
//     title: "Rutinas creadas",
//     value: 342,
//     change: 8,
//     positive: true,
//     bg: "bg-[var(--color-blue-light)]",
//     headerBg: "bg-[var(--color-blue-dark)]",
//     icon: ClipboardList,
//     iconColor: "text-[var(--color-blue-dark)]",
//   },
//   {
//     key: "publicRoutines",
//     title: "Rutinas públicas",
//     value: 98,
//     change: 3,
//     positive: false,
//     bg: "bg-[var(--color-yellow-light)]",
//     headerBg: "bg-[var(--color-yellow)]",
//     icon: Globe,
//     iconColor: "text-[var(--color-dark)]",
//   },
//   {
//     key: "premiumUsers",
//     title: "Usuarios Premium",
//     value: 37,
//     change: 21,
//     positive: true,
//     bg: "bg-[var(--color-red-light)]",
//     headerBg: "bg-[var(--color-red-dark)]",
//     icon: Gem,
//     iconColor: "text-[var(--color-red-dark)]",
//   },
// ]

// const ACTIVITY = [
//   { id: 1, text: "Nuevo usuario registrado", time: "Hace 2 min", type: "user" },
//   { id: 2, text: "Rutina pública publicada", time: "Hace 15 min", type: "routine" },
//   { id: 3, text: "Usuario activó prueba Premium", time: "Hace 1 h", type: "premium" },
//   { id: 4, text: "Comentario reportado por usuario", time: "Hace 3 h", type: "report" },
//   { id: 5, text: "Nueva categoría añadida", time: "Hace 5 h", type: "content" },
// ]

// // ─── Dashboard ───────────────────────────────────────────────
// export default function Dashboard() {

//   const [stats] = useState(STATS)
//   const [activity] = useState(ACTIVITY)
//   const [selectedStat, setSelectedStat] = useState(null)

//   const headerRef = useRef(null)
//   const statsRef = useRef(null)
//   const activityRef = useRef(null)

//   // ─── Animaciones ───────────────────────────────────────────
//   useEffect(() => {

//     animate(headerRef.current, {
//       translateY: [-20, 0],
//       opacity: [0, 1],
//       duration: 600,
//       easing: "ease-out",
//     })

//     animate(statsRef.current?.children, {
//       translateY: [40, 0],
//       opacity: [0, 1],
//       duration: 800,
//       easing: "ease-out",
//       delay: stagger(120),
//     })

//     animate(activityRef.current, {
//       translateY: [30, 0],
//       opacity: [0, 1],
//       duration: 700,
//       easing: "ease-out",
//       delay: 400,
//     })

//   }, [])


//   // ─── Loader ────────────────────────────────────────────────
//   if (!stats)
//     return (
//       <div className="min-h-screen bg-[var(--color-neutral-bg)] flex items-center justify-center">
//         <div className="flex flex-col items-center gap-3">
//           <div className="w-10 h-10 border-4 border-[var(--color-green-dark)] border-t-transparent rounded-full animate-spin" />
//           <p className="text-sm text-[var(--color-gray-custom)]">
//             Cargando dashboard...
//           </p>
//         </div>
//       </div>
//     )

//   // ─── UI ────────────────────────────────────────────────────
//   return (
//     <div className="max-w-6xl mx-auto space-y-6">

//       {/* Header */}
//       <div ref={headerRef} className="flex items-center gap-2">
//         <div className="w-8 h-8 rounded-xl bg-[var(--color-yellow-light)] flex items-center justify-center">
//           <LayoutDashboard size={18} className="text-[var(--color-yellow-dark)]" />
//         </div>
//         <div>
//           <h2 className="text-xl font-bold text-[var(--color-dark)] tracking-tight">
//             Dashboard
//           </h2>
//           <p className="text-xs text-[var(--color-gray-custom)] mt-1">
//             Resumen general de la plataforma
//           </p>
//         </div>
//       </div>

//       {/* Grid de stats */}
//       <div
//         ref={statsRef}
//         className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4"
//       >
//         {stats.map(({ key, ...stat }) => (
//           <StatCard
//             key={key}
//             {...stat}
//             onClick={() => setSelectedStat({ type: key, title: stat.title })}
//           />
//         ))}
//       </div>

//       {/* Actividad reciente */}
//       <div ref={activityRef}>
//         <ActivityList items={activity} />
//       </div>

//       {/* Modal de detalles */}
//       {selectedStat && (
//         <StatDetailsModal
//           type={selectedStat.type}
//           title={selectedStat.title}
//           onClose={() => setSelectedStat(null)}
//         />
//       )}

//     </div>
//   )
// }
