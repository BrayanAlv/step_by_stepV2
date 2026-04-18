import { useState, useEffect } from "react"
import { AuthContext } from "./AuthContext"
import * as authService from "../services/authService"

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Verificar si hay token al cargar
    const token = authService.getToken()
    if (token) {
      setIsAuthenticated(true)
      // Aquí podríamos llamar a un endpoint /me para obtener datos del usuario
      // Por ahora, asumimos que estamos logueados si hay token
    }
    setLoading(false)
  }, [])

  const login = async (email, password) => {
    const data = await authService.login(email, password)
    setIsAuthenticated(true)
    setUser(data.user || { email }) // Guardar info básica si el backend la devuelve
    return data
  }

  const register = async (userData) => {
    const data = await authService.register(userData)
    setIsAuthenticated(true)
    setUser(data.user || { email: userData.correo })
    return data
  }

  const logout = () => {
    authService.logout()
    setIsAuthenticated(false)
    setUser(null)
  }

  const value = {
    user,
    isAuthenticated,
    loading,
    login,
    register,
    logout
  }

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  )
}
