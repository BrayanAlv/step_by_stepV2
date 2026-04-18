import { Heart, MessageCircle, Share2, Trash2, User } from "lucide-react"

export default function RoutineCard({ routine, onDelete }) {
  return (
    <div className="group bg-white rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-all duration-300 overflow-hidden flex flex-col h-full">
      
      {/* Header */}
      <div className="p-4 flex items-center gap-3 border-b border-gray-50 bg-[var(--color-neutral-bg)]/30">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[var(--color-blue-light)] to-[var(--color-blue-dark)] flex items-center justify-center text-white font-bold shadow-sm">
          {routine.authorAvatar ? (
            <img src={routine.authorAvatar} alt={routine.author} className="w-full h-full rounded-full object-cover" />
          ) : (
            <User size={18} />
          )}
        </div>

        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-bold text-[var(--color-dark)] truncate">
            {routine.author}
          </h4>
          <p className="text-xs text-[var(--color-gray-custom)]">
            {routine.date || "Recién publicado"}
          </p>
        </div>

        {/* Delete */}
        <button
          onClick={(e) => {
            e.stopPropagation()
            onDelete()
          }}
          className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
          title="Eliminar rutina"
        >
          <Trash2 size={16} />
        </button>
      </div>

      {/* Body */}
      <div className="p-5 flex-1 flex flex-col gap-3">
        
        {/* Title + momento */}
        <div>
          <h3 className="text-lg font-bold text-[var(--color-dark)] line-clamp-1 mb-1">
            {routine.title}
          </h3>

          {/* 👇 ESTE ES EL PRIMER "mañana" (se queda) */}
          <p className="text-sm text-[var(--color-gray-custom)] capitalize">
            {routine.description}
          </p>
        </div>

        {/* 👇 AQUÍ VAN LOS HÁBITOS (reemplaza el segundo "mañana") */}
        <div className="flex flex-wrap gap-2 mt-auto pt-3">
          {routine.habits?.length > 0 ? (
            routine.habits.map((habit) => (
              <span
                key={habit.id}
                className="text-[10px] font-semibold tracking-wide px-2.5 py-1 rounded-full bg-[var(--color-neutral-bg)] text-[var(--color-gray-custom)]"
              >
                {habit.text}
              </span>
            ))
          ) : (
            <span className="text-xs text-gray-400">
              Sin hábitos
            </span>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="px-5 py-3 border-t border-gray-100 bg-gray-50/50 flex items-center justify-between text-xs font-medium text-[var(--color-gray-custom)]">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5 hover:text-pink-500 transition-colors cursor-pointer">
            <Heart size={14} className={routine.liked ? "fill-pink-500 text-pink-500" : ""} />
            <span>{routine.likes || 0}</span>
          </div>

          <div className="flex items-center gap-1.5 hover:text-blue-500 transition-colors cursor-pointer">
            <MessageCircle size={14} />
            <span>{routine.comments || 0}</span>
          </div>

          <div className="flex items-center gap-1.5 hover:text-green-500 transition-colors cursor-pointer">
            <Share2 size={14} />
            <span>{routine.shares || 0}</span>
          </div>
        </div>
      </div>
    </div>
  )
}
// import { Heart, MessageCircle, Share2, Trash2, User } from "lucide-react"

// export default function RoutineCard({ routine, onDelete }) {
//   return (
//     <div className="group bg-white rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-all duration-300 overflow-hidden flex flex-col h-full">
//       {/* Header: Autor y Fecha */}
//       <div className="p-4 flex items-center gap-3 border-b border-gray-50 bg-[var(--color-neutral-bg)]/30">
//         <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[var(--color-blue-light)] to-[var(--color-blue-dark)] flex items-center justify-center text-white font-bold shadow-sm">
//           {routine.authorAvatar ? (
//             <img src={routine.authorAvatar} alt={routine.author} className="w-full h-full rounded-full object-cover" />
//           ) : (
//             <User size={18} />
//           )}
//         </div>
//         <div className="flex-1 min-w-0">
//           <h4 className="text-sm font-bold text-[var(--color-dark)] truncate">
//             {routine.author}
//           </h4>
//           <p className="text-xs text-[var(--color-gray-custom)]">
//             {routine.date || "Recién publicado"}
//           </p>
//         </div>
//         {/* Acciones Admin */}
//         <button
//           onClick={(e) => {
//             e.stopPropagation()
//             onDelete()
//           }}
//           className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
//           title="Eliminar rutina"
//         >
//           <Trash2 size={16} />
//         </button>
//       </div>

//       {/* Body: Contenido */}
//       <div className="p-5 flex-1 flex flex-col gap-3">
//         <div>
//           <h3 className="text-lg font-bold text-[var(--color-dark)] line-clamp-1 mb-1">
//             {routine.title}
//           </h3>
//           <p className="text-sm text-[var(--color-gray-custom)] line-clamp-3 leading-relaxed">
//             {routine.description || "Sin descripción detallada. Esta rutina se enfoca en ejercicios de alta intensidad..."}
//           </p>
//         </div>

//         {/* Tags */}
//         <div className="flex flex-wrap gap-2 mt-auto pt-3">
//           {routine.tags?.map((tag, idx) => (
//             <span key={idx} className="text-[10px] font-semibold tracking-wide px-2.5 py-1 rounded-full bg-[var(--color-neutral-bg)] text-[var(--color-gray-custom)] uppercase">
//               {tag}
//             </span>
//           ))}
//         </div>
//       </div>

//       {/* Footer: Stats */}
//       <div className="px-5 py-3 border-t border-gray-100 bg-gray-50/50 flex items-center justify-between text-xs font-medium text-[var(--color-gray-custom)]">
//         <div className="flex items-center gap-4">
//           <div className="flex items-center gap-1.5 hover:text-pink-500 transition-colors cursor-pointer">
//             <Heart size={14} className={routine.liked ? "fill-pink-500 text-pink-500" : ""} />
//             <span>{routine.likes || 0}</span>
//           </div>
//           <div className="flex items-center gap-1.5 hover:text-blue-500 transition-colors cursor-pointer">
//             <MessageCircle size={14} />
//             <span>{routine.comments || 0}</span>
//           </div>
//           <div className="flex items-center gap-1.5 hover:text-green-500 transition-colors cursor-pointer">
//             <Share2 size={14} />
//             <span>{routine.shares || 0}</span>
//           </div>
//         </div>
//       </div>
//     </div>
//   )
// }
