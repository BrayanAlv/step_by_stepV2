import { NavLink } from "react-router-dom"
import { useState } from "react"
import {
  LayoutDashboard,
  FolderOpen,
  ShieldCheck,
  Gem,
  Settings,
  ChevronLeft,
  ChevronRight,
  UserPlus,
} from "lucide-react"

const menuItems = [
  { key: "dashboard", label: "Dashboard", icon: LayoutDashboard, to: "/admin/dashboard" },
  {
    key: "content",
    label: "Gestión de contenido",
    icon: FolderOpen,
    children: [
      { label: "Categorías", to: "/admin/content/categories" },
      { label: "Frases", to: "/admin/content/phrases" },
      // { label: "Recomendaciones", to: "/admin/content/recommendations" },
    ],
  },
  {
    key: "moderation",
    label: "Moderación",
    icon: ShieldCheck,
    children: [
      { label: "Rutinas públicas", to: "/admin/moderation/routines" },
    ],
  },
  {
    key: "registerAdmin",
    label: "Registro de admin",
    icon: UserPlus,
    to: "/registro",
  },
]

function SubItem({ to, label }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `relative flex items-center pl-4 pr-3 py-1.5 text-xs rounded-lg transition-all duration-200
        before:absolute before:left-0 before:top-1/2 before:-translate-y-1/2
        before:w-1 before:h-1 before:rounded-[1px] before:transition-all before:duration-200
        ${isActive
          ? "text-[var(--color-green-dark)] before:bg-[var(--color-green-dark)] font-semibold"
          : "text-[var(--color-gray-custom)] before:bg-[var(--color-gray-custom)] hover:text-[var(--color-dark)] hover:bg-[var(--color-neutral-bg)]"
        }`
      }
    >
      {label}
    </NavLink>
  )
}

export default function Sidebar({ collapsed, onCollapse }) {
  return (
    <aside
      className={`relative bg-white border-r border-gray-200 flex flex-col shadow-sm transition-all duration-300 ease-out ${collapsed ? "w-18" : "w-64"
        }`}
      style={{ height: "100vh", minHeight: 0 }}
    >
      {/* Logo */}
      <div className={`flex items-center pt-5 pb-4 flex-shrink-0 relative transition-all duration-300 ${collapsed ? "justify-center px-0" : "justify-between px-4"}`}>
        <div className="flex items-center gap-2.5 overflow-hidden transition-all duration-300">
          <div className="w-7 h-7 rounded-lg bg-[var(--color-green-dark)] flex items-center justify-center flex-shrink-0">
            <span className="text-white text-xs font-bold">P</span>
          </div>
          <span className={`font-bold text-sm text-[var(--color-dark)] whitespace-nowrap transition-all duration-300 ${collapsed ? "w-0 opacity-0 hidden" : "w-auto opacity-100"}`}>
            Paso a Paso
          </span>
        </div>

        <button
          onClick={() => onCollapse(!collapsed)}
          className="absolute top-5 -right-3.5 w-7 h-7 bg-white border border-gray-200 rounded-full flex items-center justify-center text-[var(--color-gray-custom)] hover:text-[var(--color-green-dark)] shadow-sm transition-all duration-200 z-10"
        >
          {collapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
        </button>
      </div>

      <div className="mx-3 border-t border-gray-100 flex-shrink-0" />

      {/* Nav — scroll interno */}
      <nav className="flex-1 flex flex-col gap-0.5 px-2.5 py-3 overflow-y-auto min-h-0">
        {menuItems.map((item) => {
          const Icon = item.icon
          const isExpandable = !!item.children

          if (!isExpandable) {
            return (
              <NavLink
                key={item.key}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200
                  ${isActive
                    ? "bg-[var(--color-green-light)] text-[var(--color-green-dark)]"
                    : "text-[var(--color-gray-custom)] hover:bg-[var(--color-neutral-bg)] hover:text-[var(--color-dark)]"
                  }`
                }
              >
                <Icon size={18} className="flex-shrink-0" />
                <span className={`whitespace-nowrap transition-all duration-300 ${collapsed ? "w-0 opacity-0 overflow-hidden" : "w-auto opacity-100"}`}>
                  {item.label}
                </span>
              </NavLink>
            )
          }

          return (
            <div key={item.key}>
              <div
                className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-[var(--color-gray-custom)] transition-all duration-200"
              >
                <Icon size={18} className="flex-shrink-0" />
                <span className={`whitespace-nowrap flex-1 text-left transition-all duration-300 ${collapsed ? "w-0 opacity-0 overflow-hidden" : "w-auto opacity-100"}`}>
                  {item.label}
                </span>
              </div>

              <div className={`overflow-hidden transition-all duration-300 ease-out ${!collapsed ? "max-h-96 opacity-100 mt-1" : "max-h-0 opacity-0"}`}>
                <div className="ml-3 flex flex-col gap-0.5 border-l-2 border-gray-100 pl-3">
                  {item.children.map((child) => (
                    <SubItem key={child.to} {...child} />
                  ))}
                </div>
              </div>
            </div>
          )
        })}
      </nav>

      {/* Footer */}
      <div className={`flex-shrink-0 border-t border-gray-100 pt-3 pb-2 transition-all duration-300 ${collapsed ? "mx-1" : "mx-3"}`}>
        <div className={`flex items-center gap-3 px-2 py-2 rounded-xl hover:bg-[var(--color-neutral-bg)] transition cursor-pointer ${collapsed ? "justify-center" : ""}`}>
          <div className="w-7 h-7 rounded-full bg-[var(--color-blue-light)] flex items-center justify-center flex-shrink-0">
            <span className="text-[var(--color-blue-dark)] text-xs font-bold">A</span>
          </div>
          <span className={`text-xs font-medium text-[var(--color-dark)] whitespace-nowrap transition-all duration-300 ${collapsed ? "w-0 opacity-0 overflow-hidden hidden" : "w-auto opacity-100"}`}>
            Admin
          </span>
        </div>
      </div>
    </aside>
  )
}