import { X, MessageCircle, Heart, User, Calendar } from "lucide-react"
import { useEffect, useRef, useState } from "react"
import { animate } from "animejs"

export default function RoutineDetailModal({ routine, onClose }) {
    const modalRef = useRef(null)
    const contentRef = useRef(null)

    const [comments, setComments] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        if (!routine) return

        // Animaciones
        animate(modalRef.current, {
            opacity: [0, 1],
            duration: 300,
            easing: "easeOutQuad"
        })

        animate(contentRef.current, {
            scale: [0.9, 1],
            opacity: [0, 1],
            translateY: [20, 0],
            duration: 400,
            delay: 100,
            easing: "easeOutExpo"
        })

        fetchComments()

    }, [routine])

    // 🔥 FETCH DE COMENTARIOS + USUARIOS
    const fetchComments = async () => {
        try {
            setLoading(true)

            const res = await fetch(
                `https://stepbystep.cv/api/v1/comunidad/comentarios/${routine.id}`
            )

            const data = await res.json()

            // 🔥 Obtener nombres de usuarios
            const formatted = await Promise.all(
                data.map(async (c) => {
                    try {
                        const userRes = await fetch(
                            `https://stepbystep.cv/api/v1/usuarios/${c.usuario_id}`
                        )
                        const userData = await userRes.json()

                        return {
                            id: c.id,
                            user: userData.nombre || `Usuario ${c.usuario_id}`,
                            text: c.contenido,
                            date: new Date(c.fecha).toLocaleString()
                        }

                    } catch {
                        return {
                            id: c.id,
                            user: `Usuario ${c.usuario_id}`,
                            text: c.contenido,
                            date: new Date(c.fecha).toLocaleString()
                        }
                    }
                })
            )

            setComments(formatted)

        } catch (error) {
            console.error("Error cargando comentarios:", error)
            setComments([])
        } finally {
            setLoading(false)
        }
    }

    const handleClose = () => {
        onClose()
    }

    if (!routine) return null

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            {/* Backdrop */}
            <div
                ref={modalRef}
                onClick={handleClose}
                className="absolute inset-0 bg-black/40 backdrop-blur-sm"
            />

            {/* Modal */}
            <div
                ref={contentRef}
                className="relative bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[85vh] flex flex-col overflow-hidden"
            >
                {/* Header */}
                <div className="relative h-32 bg-gradient-to-r from-[var(--color-blue-dark)] to-purple-600 flex items-end p-6">
                    <button
                        onClick={handleClose}
                        className="absolute top-4 right-4 p-2 bg-black/20 hover:bg-black/40 text-white rounded-full"
                    >
                        <X size={20} />
                    </button>

                    <div className="flex items-center gap-4 text-white translate-y-8">
                        <div className="w-20 h-20 rounded-2xl bg-white p-1 shadow-lg">
                            <div className="w-full h-full rounded-xl bg-gray-100 flex items-center justify-center">
                                <User size={32} className="text-gray-400" />
                            </div>
                        </div>

                        <div className="mb-2">
                            <h2 className="text-2xl font-bold">{routine.title}</h2>
                            <p className="text-white/80 text-sm flex items-center gap-2">
                                Por {routine.author} • <Calendar size={12} /> {routine.date}
                            </p>
                        </div>
                    </div>
                </div>

                {/* Body */}
                <div className="flex-1 overflow-y-auto pt-10 px-6 pb-6">

                    {/* Stats */}
                    <div className="flex gap-4 mb-6 border-b pb-4">
                        <div className="flex items-center gap-1.5 text-pink-500 font-semibold text-sm">
                            <Heart size={16} fill="currentColor" />
                            {routine.likes} Likes
                        </div>

                        <div className="flex items-center gap-1.5 text-blue-500 font-semibold text-sm">
                            <MessageCircle size={16} />
                            {comments.length} Comentarios
                        </div>
                    </div>

                    {/* Comentarios */}
                    <section className="pt-4 border-t border-gray-100">
                        <h3 className="text-sm font-bold text-[var(--color-gray-custom)] uppercase mb-4">
                            Comentarios
                        </h3>

                        {loading ? (
                            <p className="text-sm text-gray-400">Cargando comentarios...</p>
                        ) : comments.length === 0 ? (
                            <p className="text-sm text-gray-400">No hay comentarios</p>
                        ) : (
                            <div className="space-y-4">
                                {comments.map((comment) => (
                                    <div key={comment.id} className="flex gap-3">
                                        <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-gray-500 font-bold">
                                            {comment.user.charAt(0)}
                                        </div>

                                        <div className="bg-gray-50 rounded-2xl rounded-tl-none p-3 flex-1">
                                            <div className="flex justify-between mb-1">
                                                <span className="font-bold text-xs">
                                                    {comment.user}
                                                </span>
                                                <span className="text-[10px] text-gray-400">
                                                    {comment.date}
                                                </span>
                                            </div>

                                            <p className="text-sm text-gray-600">
                                                {comment.text}
                                            </p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </section>
                </div>
            </div>
        </div>
    )
}