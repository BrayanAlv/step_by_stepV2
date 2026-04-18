import { useEffect, useRef, useState } from "react"
import { animate } from "animejs"
import { Sparkles, User } from "lucide-react"
import RecommendationEditor from "../../../components/admin/content/RecommendationEditor"

export default function Recommendations() {
  const [mode, setMode] = useState("manual")
  const headerRef = useRef(null)
  const modesRef = useRef(null)
  const contentRef = useRef(null)

  useEffect(() => {

    animate(headerRef.current, {
      translateY: [-20, 0],
      opacity: [0, 1],
      duration: 500,
      easing: "ease-out",
    })

    animate(modesRef.current?.children, {
      scale: [0.9, 1],
      opacity: [0, 1],
      delay: 150,
      duration: 400,
    })

  }, [])

  useEffect(() => {

    animate(contentRef.current, {
      opacity: [0, 1],
      translateY: [15, 0],
      duration: 400,
      easing: "ease-out",
    })

  }, [mode])


  return (
    <div className="mx-auto space-y-5">
      {/* Header */}
      <div ref={headerRef}>
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-[var(--color-red-light)] flex items-center justify-center">
            <Sparkles size={16} className="text-[var(--color-red-dark)]" />
          </div>
          <h2 className="text-xl font-bold text-[var(--color-dark)] tracking-tight">
            Recomendaciones
          </h2>
        </div>
        <p className="text-xs text-[var(--color-gray-custom)] mt-1 ml-10">
          Configura cómo se generan las recomendaciones de rutinas
        </p>
      </div>

      {/* Card principal */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
        {/* Header card */}
        <div className="bg-[var(--color-neutral-light)] border-b border-gray-100 px-5 py-3">
          <h3 className="text-xs font-semibold text-[var(--color-gray-custom)] uppercase tracking-widest">
            Modo de generación
          </h3>
        </div>

        <div className="p-5 space-y-5">
          {/* Selector de modo — dos cards clickables */}
          <div ref={modesRef} className="grid grid-cols-2 gap-3">
            {/* Manual */}
            <button
              onClick={() => setMode("manual")}
              className={`
                relative flex flex-col items-start gap-1.5 p-4 rounded-xl border-2 text-left
                transition-all duration-200
                ${mode === "manual"
                  ? "border-[var(--color-blue-dark)] bg-[var(--color-blue-light)]"
                  : "border-gray-200 bg-[var(--color-neutral-light)] hover:border-gray-300"
                }
              `}
            >
              {/* Badge activo */}
              {mode === "manual" && (
                <span className="absolute top-2.5 right-2.5 text-xs font-semibold bg-[var(--color-blue-dark)] text-white px-2 py-0.5 rounded-full">
                  Activo
                </span>
              )}
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${mode === "manual" ? "bg-white" : "bg-[var(--color-neutral-bg)]"
                }`}>
                <User size={16} className={mode === "manual" ? "text-[var(--color-blue-dark)]" : "text-[var(--color-gray-custom)]"} />
              </div>
              <p className={`text-sm font-semibold ${mode === "manual" ? "text-[var(--color-blue-dark)]" : "text-[var(--color-dark)]"}`}>
                Manual
              </p>
              <p className="text-xs text-[var(--color-gray-custom)]">
                Tú defines las rutinas recomendadas
              </p>
            </button>

            {/* IA */}
            <button
              onClick={() => setMode("ia")}
              className={`
                relative flex flex-col items-start gap-1.5 p-4 rounded-xl border-2 text-left
                transition-all duration-200
                ${mode === "ia"
                  ? "border-[var(--color-red-dark)] bg-[var(--color-red-light)]"
                  : "border-gray-200 bg-[var(--color-neutral-light)] hover:border-gray-300"
                }
              `}
            >
              {mode === "ia" && (
                <span className="absolute top-2.5 right-2.5 text-xs font-semibold bg-[var(--color-red-dark)] text-white px-2 py-0.5 rounded-full">
                  Activo
                </span>
              )}
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${mode === "ia" ? "bg-white" : "bg-[var(--color-neutral-bg)]"
                }`}>
                <Sparkles size={16} className={mode === "ia" ? "text-[var(--color-red-dark)]" : "text-[var(--color-gray-custom)]"} />
              </div>
              <p className={`text-sm font-semibold ${mode === "ia" ? "text-[var(--color-red-dark)]" : "text-[var(--color-dark)]"}`}>
                Inteligencia Artificial
              </p>
              <p className="text-xs text-[var(--color-gray-custom)]">
                Se generan automáticamente con IA
              </p>
            </button>
          </div>

          {/* Contenido según modo */}
          <div ref={contentRef} className={`rounded-xl border overflow-hidden transition-all duration-300`}>
            {mode === "manual" ? (
              <RecommendationEditor />
            ) : (
              <div className="bg-[var(--color-red-light)] border border-[var(--color-red-dark)] rounded-xl p-5">
                <div className="flex items-start gap-3">
                  <div className="w-9 h-9 rounded-xl bg-white flex items-center justify-center flex-shrink-0 shadow-sm">
                    <Sparkles size={18} className="text-[var(--color-red-dark)]" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-[var(--color-dark)]">
                      Modo IA activado
                    </p>
                    <p className="text-xs text-[var(--color-gray-custom)] mt-0.5">
                      Las recomendaciones se generarán automáticamente basándose en el historial y preferencias de cada usuario. No se requiere configuración adicional.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}