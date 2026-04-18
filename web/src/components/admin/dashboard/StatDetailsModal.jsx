import { X, User, ClipboardList, Globe, Gem } from "lucide-react"
import { useEffect, useRef, useState } from "react"
import { animate } from "animejs"
import DataTable from "./DataTable"

const MOCK_DATA = {
    users: {
        columns: [
            { header: "ID", accessor: "id" },
            { header: "Nombre", accessor: "name" },
            { header: "Email", accessor: "email" },
            {
                header: "Suscripción",
                accessor: "role",
                render: (val) => (
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${val === "Premium"
                        ? "bg-yellow-100 text-yellow-700"
                        : "bg-blue-100 text-blue-600"
                        }`}>
                        {val}
                    </span>
                )
            }
        ],
        data: []
    },
    routines: {
        columns: [
            { header: "Nombre", accessor: "title" },
            { header: "Momento", accessor: "momento" },
            { header: "Hábitos", accessor: "habitos" },
            { 
                header: "Visibilidad", 
                accessor: "es_publica",
                render: (val) => (
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        val ? "bg-green-100 text-green-600" : "bg-gray-100 text-gray-600"
                    }`}>
                        {val ? "Pública" : "Privada"}
                    </span>
                )
            },
            { header: "Fecha", accessor: "date" }
        ],
        data: []
    },
    publicRoutines: {
        columns: [
            { header: "Rutina", accessor: "title" },
            { header: "Momento", accessor: "momento" },
            { header: "Hábitos", accessor: "habitos" },
            { header: "Rating / Likes", accessor: "rating_y_likes" },
            { header: "Fecha", accessor: "date" }
        ],
        data: []
    },
    premiumUsers: {
        columns: [
            { header: "Usuario", accessor: "name" },
            { header: "Email", accessor: "email" },
            { header: "Plan", accessor: "plan" },
            { header: "Vencimiento", accessor: "expiry" },
            {
                header: "Estado",
                accessor: "active",
                render: (val) => (
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        val ? "bg-green-100 text-green-600" : "bg-red-100 text-red-600"
                    }`}>
                        {val ? "Activo" : "Inactivo"}
                    </span>
                )
            }
        ],
        data: []
    }
}

const ICONS = {
    users: User,
    routines: ClipboardList,
    publicRoutines: Globe,
    premiumUsers: Gem
}

export default function StatDetailsModal({ type, title, onClose }) {

    const modalRef = useRef(null)
    const contentRef = useRef(null)

    const [apiUsers, setApiUsers] = useState([])
    const [apiPremiumUsers, setApiPremiumUsers] = useState([])
    const [apiRoutines, setApiRoutines] = useState([])
    const [apiPublicRoutines, setApiPublicRoutines] = useState([])
    const [loading, setLoading] = useState(false)

    const Icon = ICONS[type] || User

    // Animaciones
    useEffect(() => {
        animate(modalRef.current, {
            opacity: [0, 1],
            duration: 300,
            easing: "easeOutQuad"
        })

        animate(contentRef.current, {
            scale: [0.95, 1],
            opacity: [0, 1],
            translateY: [20, 0],
            duration: 400,
            easing: "easeOutExpo"
        })
    }, [])

    // 🔥 FETCH DINÁMICO
    useEffect(() => {

        const fetchData = async () => {
            try {
                setLoading(true)

                // USERS
                if (type === "users") {
                    try {
                        setLoading(true)

                        const res = await fetch("https://stepbystep.cv/api/v1/usuarios/freemium/all?skip=0&limit=10")
                        const data = await res.json()

                        const usersArray = data.data || data || []

                        const formatted = usersArray.map(user => ({
                            id: user.id || "-",
                            name: user.nombre || user.name || "-",
                            email: user.correo_electronico || user.email || "-",
                            role: user.es_premium ? "Premium" : "Gratuito"
                        }))

                        setApiUsers(formatted)

                    } catch (err) {
                        console.error(err)
                    } finally {
                        setLoading(false)
                    }
                }

                // PREMIUM USERS
                if (type === "premiumUsers") {
                    const res = await fetch("https://stepbystep.cv/api/v1/usuarios/premium/all")
                    const data = await res.json()

                    const usersArray = data.data || data || []

                    const formatted = usersArray.map(user => ({
                        name: user.nombre || user.name,
                        email: user.correo_electronico || user.email,
                        plan: user.plan_nombre || user.tipo_suscripcion_pagada || "Premium",
                        expiry: user.fecha_fin_suscripcion 
                            ? new Date(user.fecha_fin_suscripcion).toLocaleDateString() 
                            : "-",
                        active: user.es_suscripcion_activa
                    }))

                    setApiPremiumUsers(formatted)
                }

                // ROUTINES
                if (type === "routines" || type === "publicRoutines") {
                    const res = await fetch("https://stepbystep.cv/api/v1/rutinas/?skip=0&limit=100")
                    const data = await res.json()

                    const routinesArray = data.data || data || []

                    const allFormatted = routinesArray.map(r => ({
                        title: r.nombre || r.title,
                        momento: r.momento_dia ? (r.momento_dia.charAt(0).toUpperCase() + r.momento_dia.slice(1)) : "-",
                        habitos: Array.isArray(r.habitos) ? r.habitos.length : 0,
                        es_publica: r.es_publica,
                        date: r.created_at ? new Date(r.created_at).toLocaleDateString() : "-"
                    }))

                    const publicFormatted = routinesArray
                        .filter(r => r.es_publica === true)
                        .map(r => ({
                            title: r.nombre || r.title,
                            momento: r.momento_dia ? (r.momento_dia.charAt(0).toUpperCase() + r.momento_dia.slice(1)) : "-",
                            habitos: Array.isArray(r.habitos) ? r.habitos.length : 0,
                            rating_y_likes: `⭐ ${Number(r.rating_promedio || 0).toFixed(1)} / ❤️ ${r.total_likes || 0}`,
                            date: r.created_at ? new Date(r.created_at).toLocaleDateString() : "-"
                        }))

                    setApiRoutines(allFormatted)
                    setApiPublicRoutines(publicFormatted)
                }

            } catch (err) {
                console.error("Error modal:", err)
            } finally {
                setLoading(false)
            }
        }

        fetchData()

    }, [type])

    // 🔥 DATA FINAL
    let details = MOCK_DATA[type] || { columns: [], data: [] }

    if (type === "users") {
        details = { columns: MOCK_DATA.users.columns, data: apiUsers }
    }

    if (type === "premiumUsers") {
        details = { columns: MOCK_DATA.premiumUsers.columns, data: apiPremiumUsers }
    }

    if (type === "routines") {
        details = { columns: MOCK_DATA.routines.columns, data: apiRoutines }
    }

    if (type === "publicRoutines") {
        details = { columns: MOCK_DATA.publicRoutines.columns, data: apiPublicRoutines }
    }

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">

            <div
                ref={modalRef}
                onClick={onClose}
                className="absolute inset-0 bg-black/40 backdrop-blur-sm"
            />

            <div
                ref={contentRef}
                className="relative bg-white rounded-3xl shadow-2xl w-full max-w-2xl overflow-hidden flex flex-col max-h-[85vh]"
            >

                <div className="p-6 flex items-center justify-between border-b border-gray-100">
                    <div className="flex items-center gap-4">
                        <div className="p-3 bg-gray-100 rounded-2xl">
                            <Icon size={24} />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold">{title}</h2>
                            <p className="text-xs text-gray-400 uppercase">
                                Detalle de registros
                            </p>
                        </div>
                    </div>

                    <button onClick={onClose}>
                        <X />
                    </button>
                </div>

                <div className="flex-1 overflow-y-auto p-4">
                    {loading ? (
                        <p className="text-center">Cargando...</p>
                    ) : (
                        <DataTable columns={details.columns} data={details.data} />
                    )}
                </div>

                <div className="p-4 text-center text-xs text-gray-400">
                    Paso-a-Paso Admin Panel • 2026
                </div>
            </div>
        </div>
    )
}

// import { X, User, ClipboardList, Globe, Gem } from "lucide-react"
// import { useEffect, useRef } from "react"
// import { animate } from "animejs"
// import DataTable from "./DataTable"

// const MOCK_DATA = {
//     users: {
//         columns: [
//             { header: "ID", accessor: "id" },
//             { header: "Nombre", accessor: "name" },
//             { header: "Email", accessor: "email" },
//             {
//                 header: "Rol", accessor: "role", render: (val) => (
//                     <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${val === 'Admin' ? 'bg-purple-100 text-purple-600' : 'bg-blue-100 text-blue-600'}`}>
//                         {val}
//                     </span>
//                 )
//             },
//         ],
//         data: [
//             { id: "#001", name: "Anita", email: "anita@pasoapaso.com", role: "Admin" },
//             { id: "#002", name: "Juan Pérez", email: "juan@gmail.com", role: "Usuario" },
//             { id: "#003", name: "Maria L.", email: "maria@outlook.com", role: "Usuario" },
//         ]
//     },
//     routines: {
//         columns: [
//             { header: "Nombre", accessor: "title" },
//             { header: "Autor", accessor: "author" },
//             { header: "Likes", accessor: "likes" },
//             { header: "Fecha", accessor: "date" },
//         ],
//         data: [
//             { title: "Yoga Matutino", author: "Roberto G.", likes: 45, date: "20/02/2026" },
//             { title: "HIIT Intenso", author: "Carlos Gym", likes: 128, date: "19/02/2026" },
//             { title: "Estiramiento", author: "Lucia S.", likes: 23, date: "18/02/2026" },
//         ]
//     },
//     publicRoutines: {
//         columns: [
//             { header: "Rutina", accessor: "title" },
//             { header: "Categoría", accessor: "category" },
//             { header: "Vistas", accessor: "views" },
//         ],
//         data: [
//             { title: "Meditación Guiada", category: "Mindfulness", views: 1240 },
//             { title: "Core 15 min", category: "Fitness", views: 890 },
//             { title: "Power Yoga", category: "Yoga", views: 3400 },
//         ]
//     },
//     premiumUsers: {
//         columns: [
//             { header: "Usuario", accessor: "name" },
//             { header: "Plan", accessor: "plan" },
//             { header: "Vencimiento", accessor: "expiry" },
//         ],
//         data: [
//             { name: "Sonia Fit", plan: "Anual", expiry: "12/12/2026" },
//             { name: "Marco Polo", plan: "Mensual", expiry: "05/03/2026" },
//             { name: "Elena Q.", plan: "Anual", expiry: "20/01/2027" },
//         ]
//     }
// }

// const ICONS = {
//     users: User,
//     routines: ClipboardList,
//     publicRoutines: Globe,
//     premiumUsers: Gem
// }

// export default function StatDetailsModal({ type, title, onClose }) {
//     const modalRef = useRef(null)
//     const contentRef = useRef(null)
//     const Icon = ICONS[type] || User

//     useEffect(() => {
//         animate(modalRef.current, {
//             opacity: [0, 1],
//             duration: 300,
//             easing: "easeOutQuad"
//         })

//         animate(contentRef.current, {
//             scale: [0.95, 1],
//             opacity: [0, 1],
//             translateY: [20, 0],
//             duration: 400,
//             easing: "easeOutExpo"
//         })
//     }, [])

//     const details = MOCK_DATA[type] || { columns: [], data: [] }

//     return (
//         <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
//             {/* Backdrop */}
//             <div
//                 ref={modalRef}
//                 onClick={onClose}
//                 className="absolute inset-0 bg-black/40 backdrop-blur-sm"
//             />

//             {/* Content */}
//             <div
//                 ref={contentRef}
//                 className="relative bg-white rounded-3xl shadow-2xl w-full max-w-2xl overflow-hidden flex flex-col max-h-[85vh]"
//             >
//                 {/* Header */}
//                 <div className="p-6 flex items-center justify-between border-b border-gray-100 bg-gray-50/10">
//                     <div className="flex items-center gap-4">
//                         <div className="p-3 bg-[var(--color-neutral-bg)] rounded-2xl text-[var(--color-dark)] shadow-sm">
//                             <Icon size={24} />
//                         </div>
//                         <div>
//                             <h2 className="text-xl font-bold text-[var(--color-dark)]">{title}</h2>
//                             <p className="text-xs text-[var(--color-gray-custom)] font-medium uppercase tracking-wider mt-0.5">
//                                 Detalle de registros recientes
//                             </p>
//                         </div>
//                     </div>
//                     <button
//                         onClick={onClose}
//                         className="p-2.5 hover:bg-gray-100 text-gray-400 hover:text-gray-600 rounded-xl transition-all"
//                     >
//                         <X size={20} />
//                     </button>
//                 </div>

//                 {/* Scrollable Table */}
//                 <div className="flex-1 overflow-y-auto p-4">
//                     <div className="rounded-2xl border border-gray-100 overflow-hidden shadow-sm bg-white">
//                         <DataTable columns={details.columns} data={details.data} />
//                     </div>
//                 </div>

//                 {/* Footer */}
//                 <div className="p-4 bg-gray-50/50 border-t border-gray-100 text-center">
//                     <p className="text-[10px] text-[var(--color-gray-custom)] font-medium">
//                         Paso-a-Paso Admin Panel • 2026
//                     </p>
//                 </div>
//             </div>
//         </div>
//     )
// }
