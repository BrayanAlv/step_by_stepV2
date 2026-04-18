import { Routes, Route, Navigate } from "react-router-dom"

import Landing from "./pages/Landing"
import Login from "./pages/Admin/AdminLogin"
import Registro from "./pages/Admin/Register"

import AdminLayout from "./layouts/AdminLayout"
import Dashboard from "./pages/Admin/Dashboard"
import Categories from "./pages/Admin/content/Categories"
import Recommendations from "./pages/Admin/content/Recommendations"
import MotivationalPhrases from "./pages/Admin/content/MotivationalPhrases"
import PublicRoutines from "./pages/Admin/moderation/PublicRoutines"

export default function App() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/registro" element={<Registro />} />

      <Route path="/admin" element={<AdminLayout />}>
        <Route path="*" element={<Navigate to="dashboard" />} />

        <Route path="dashboard" element={<Dashboard />} />
        <Route path="content/categories" element={<Categories />} />
        <Route path="content/recommendations" element={<Recommendations />} />
        <Route path="content/phrases" element={<MotivationalPhrases />} />
        <Route path="moderation/routines" element={<PublicRoutines />} />
      </Route>
    </Routes>
  )
}
