import { useEffect, useRef, useState } from "react"
import { Tag } from "lucide-react"
import { animate, stagger } from "animejs"
import CategoryForm from "../../../components/admin/content/CategoryForm"
import CategoryList from "../../../components/admin/content/CategoryList"

const TAG_COLORS = [
  { bg: "bg-[var(--color-green-light)]", text: "text-[var(--color-green-dark)]", border: "border-[var(--color-green-dark)]" },
  { bg: "bg-[var(--color-blue-light)]", text: "text-[var(--color-blue-dark)]", border: "border-[var(--color-blue-dark)]" },
  { bg: "bg-[var(--color-yellow-light)]", text: "text-[var(--color-dark)]", border: "border-[var(--color-yellow)]" },
  { bg: "bg-[var(--color-red-light)]", text: "text-[var(--color-red-dark)]", border: "border-[var(--color-red-dark)]" },
]

export default function Categories() {
  const [categories, setCategories] = useState([])

  const headerRef = useRef(null)
  const formRef = useRef(null)
  const listRef = useRef(null)

  useEffect(() => {

    // 🔹 Animaciones
    animate(headerRef.current, {
      translateY: [-20, 0],
      opacity: [0, 1],
      duration: 500,
      easing: "ease-out",
    })

    animate(formRef.current, {
      translateY: [20, 0],
      opacity: [0, 1],
      duration: 500,
      delay: 150,
      easing: "ease-out",
    })

    // 🔹 Fetch de categorías desde API
    fetch("https://stepbystep.cv/api/v1/rutinas/categorias")
      .then(res => res.json())
      .then(data => {
        const formatted = data.map(cat => ({
          id: cat.id,
          name: cat.nombre, // 👈 aquí transformas
          emoji: "🏷️", // puedes cambiarlo si quieres dinámico después
          habits: []
        }))
        setCategories(formatted)

        // Animación después de cargar
        setTimeout(() => {
          animate(listRef.current?.children, {
            translateY: [25, 0],
            opacity: [0, 1],
            duration: 600,
            delay: stagger(100),
            easing: "ease-out",
          })
        }, 100)
      })
      .catch(err => console.error("Error cargando categorías:", err))

  }, [])

  const addCategory = ({ name, emoji }) => {
    setCategories(prev => [
      ...prev,
      { id: Date.now(), name, emoji, habits: [] }
    ])
  }

  const deleteCategory = async (id) => {
    try {
      const response = await fetch(`https://stepbystep.cv/api/v1/rutinas/categorias/${id}`, {
        method: 'DELETE',
      })
      if (response.ok) {
        setCategories(prev => prev.filter(c => c.id !== id))
      } else {
        console.error("Error eliminando categoría")
      }
    } catch (error) {
      console.error("Error:", error)
    }
  }

  const addHabit = (catId, habitName) => {
    setCategories(prev =>
      prev.map(cat =>
        cat.id === catId
          ? { ...cat, habits: [...cat.habits, { id: Date.now(), name: habitName }] }
          : cat
      )
    )
  }

  const deleteHabit = (catId, habitId) => {
    setCategories(prev =>
      prev.map(cat =>
        cat.id === catId
          ? { ...cat, habits: cat.habits.filter(h => h.id !== habitId) }
          : cat
      )
    )
  }

  return (
    <div className="mx-auto space-y-5">

      <div ref={headerRef} className="flex items-center gap-2">
        <div className="w-8 h-8 rounded-xl bg-[var(--color-green-light)] flex items-center justify-center">
          <Tag size={16} className="text-[var(--color-green-dark)]" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-[var(--color-dark)]">
            Categorías
          </h2>
          <p className="text-xs text-[var(--color-gray-custom)] mt-1">
            Organiza tus hábitos en categorías
          </p>
        </div>
      </div>

      <div ref={formRef}>
        <CategoryForm onAdd={addCategory} />
      </div>

      <div ref={listRef}>
        <CategoryList
          categories={categories}
          onDelete={deleteCategory}
          onAddHabit={addHabit}
          onDeleteHabit={deleteHabit}
          colors={TAG_COLORS}
        />
      </div>

    </div>
  )
}
// import { useEffect, useRef, useState } from "react"
// import { Tag } from "lucide-react"
// import { animate, stagger } from "animejs"
// import CategoryForm from "../../../components/admin/content/CategoryForm"
// import CategoryList from "../../../components/admin/content/CategoryList"

// const INITIAL_CATEGORIES = [
//   { id: 1, name: "Salud", emoji: "🏥", habits: [] },
//   { id: 2, name: "Estudio", emoji: "📚", habits: [] },
//   { id: 3, name: "Bienestar", emoji: "🌿", habits: [] },
//   { id: 4, name: "Ejercicio", emoji: "🏋️", habits: [] },
// ]

// const TAG_COLORS = [
//   { bg: "bg-[var(--color-green-light)]", text: "text-[var(--color-green-dark)]", border: "border-[var(--color-green-dark)]" },
//   { bg: "bg-[var(--color-blue-light)]", text: "text-[var(--color-blue-dark)]", border: "border-[var(--color-blue-dark)]" },
//   { bg: "bg-[var(--color-yellow-light)]", text: "text-[var(--color-dark)]", border: "border-[var(--color-yellow)]" },
//   { bg: "bg-[var(--color-red-light)]", text: "text-[var(--color-red-dark)]", border: "border-[var(--color-red-dark)]" },
// ]

// export default function Categories() {
//   const [categories, setCategories] = useState(INITIAL_CATEGORIES)

//   const headerRef = useRef(null)
//   const formRef = useRef(null)
//   const listRef = useRef(null)

//   useEffect(() => {

//     animate(headerRef.current, {
//       translateY: [-20, 0],
//       opacity: [0, 1],
//       duration: 500,
//       easing: "ease-out",
//     })

//     animate(formRef.current, {
//       translateY: [20, 0],
//       opacity: [0, 1],
//       duration: 500,
//       delay: 150,
//       easing: "ease-out",
//     })

//     animate(listRef.current?.children, {
//       translateY: [25, 0],
//       opacity: [0, 1],
//       duration: 600,
//       delay: stagger(100),
//       easing: "ease-out",
//     })

//   }, [])

//   const addCategory = ({ name, emoji }) => {
//     setCategories(prev => [
//       ...prev,
//       { id: Date.now(), name, emoji, habits: [] }
//     ])
//   }

//   const deleteCategory = (id) => {
//     setCategories(prev => prev.filter(c => c.id !== id))
//   }

//   const addHabit = (catId, habitName) => {
//     setCategories(prev =>
//       prev.map(cat =>
//         cat.id === catId
//           ? { ...cat, habits: [...cat.habits, { id: Date.now(), name: habitName }] }
//           : cat
//       )
//     )
//   }

//   const deleteHabit = (catId, habitId) => {
//     setCategories(prev =>
//       prev.map(cat =>
//         cat.id === catId
//           ? { ...cat, habits: cat.habits.filter(h => h.id !== habitId) }
//           : cat
//       )
//     )
//   }

//   return (
//     <div className="mx-auto space-y-5">

//       <div ref={headerRef} className="flex items-center gap-2">
//         <div className="w-8 h-8 rounded-xl bg-[var(--color-green-light)] flex items-center justify-center">
//           <Tag size={16} className="text-[var(--color-green-dark)]" />
//         </div>
//         <div>
//           <h2 className="text-xl font-bold text-[var(--color-dark)]">
//             Categorías
//           </h2>
//           <p className="text-xs text-[var(--color-gray-custom)] mt-1">
//             Organiza tus hábitos en categorías
//           </p>
//         </div>
//       </div>

//       <div ref={formRef}>
//         <CategoryForm onAdd={addCategory} />
//       </div>

//       <div ref={listRef}>
//         <CategoryList
//           categories={categories}
//           onDelete={deleteCategory}
//           onAddHabit={addHabit}
//           onDeleteHabit={deleteHabit}
//           colors={TAG_COLORS}
//         />
//       </div>

//     </div>
//   )
// }