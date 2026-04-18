import { useNavigate } from "react-router-dom"
import { LogOut, Menu } from "lucide-react"

export default function Header({ onToggleSidebar }) {
  const navigate = useNavigate()

  const handleLogout = () => {
    navigate("/")
  }

  return (
    <header className="h-16 bg-white border-b border-gray-200 px-5 flex items-center justify-between shadow-sm sticky top-0 z-30">
      {/* Izquierda */}
      <div className="flex items-center gap-3">
        {/* Botón hamburguesa para mobile */}
        <button
          onClick={onToggleSidebar}
          className="lg:hidden w-8 h-8 flex items-center justify-center rounded-lg text-[var(--color-gray-custom)] hover:bg-[var(--color-neutral-bg)] hover:text-[var(--color-dark)] transition-colors duration-200"
        >
          <Menu size={18} />
        </button>

        <div>
          <h1 className="text-sm font-bold text-[var(--color-dark)] tracking-tight">
            Panel de Administración
          </h1>
          <p className="text-xs text-[var(--color-gray-custom)]">
            Bienvenido de vuelta, Admin
          </p>
        </div>
      </div>

      {/* Derecha */}
      <div className="flex items-center gap-3">
        {/* Avatar */}
        <div className="w-8 h-8 rounded-full bg-[var(--color-blue-light)] flex items-center justify-center">
          <span className="text-[var(--color-blue-dark)] text-xs font-bold">A</span>
        </div>

        {/* Logout */}
        <button
          onClick={handleLogout}
          className="flex items-center gap-1.5 text-xs font-semibold text-[var(--color-red-dark)] hover:bg-[var(--color-red-light)] px-3 py-1.5 rounded-lg transition-all duration-200"
        >
          <LogOut size={13} />
          Cerrar sesión
        </button>
      </div>
    </header>
  )
}