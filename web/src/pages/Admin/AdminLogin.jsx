import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Heart, Mail, Lock, ArrowLeft, Eye, EyeOff, Loader2 } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const LoginPage = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const [formData, setFormData] = useState({
    correo: '',
    contrasena: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      await login(formData.correo, formData.contrasena);
      navigate('/admin/dashboard');
    } catch (err) {
      setError(err.message || 'Error al iniciar sesión. Verifica tus credenciales.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    // Limpiar error al escribir
    if (error) setError('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-light/30 to-blue-light/30 relative">
      {/* Botón volver */}
      <button
        onClick={() => navigate('/')}
        className="absolute top-6 left-6 flex items-center space-x-2 text-dark hover:text-green-dark transition-colors group z-10"
      >
        <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
        <span className="font-medium">Volver al inicio</span>
      </button>

      <div className="flex items-center justify-center min-h-screen px-4 py-12">
        <div className="grid md:grid-cols-2 gap-8 max-w-5xl w-full items-center">
          {/* Imagen ilustrativa */}
          <div className="hidden md:block">
            <div className="bg-gradient-to-br from-green-dark to-blue-dark rounded-3xl p-12 shadow-2xl">
              <div className="text-white space-y-6">
                <div className="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center mb-8">
                  <Heart className="w-10 h-10 text-white" />
                </div>
                <h3 className="text-4xl font-bold">¡Nos alegra verte de vuelta!</h3>
                <p className="text-green-light text-lg leading-relaxed">
                  Continúa construyendo tus hábitos saludables y alcanzando tus metas, un paso a la vez.
                </p>

                <div className="space-y-4 pt-6">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-green-light/30 rounded-lg flex items-center justify-center">
                      <span className="text-2xl">📊</span>
                    </div>
                    <div>
                      <p className="font-semibold">Revisa tu progreso</p>
                      <p className="text-sm text-green-light">Ve tus estadísticas y logros</p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-blue-light/30 rounded-lg flex items-center justify-center">
                      <span className="text-2xl">✅</span>
                    </div>
                    <div>
                      <p className="font-semibold">Continúa tus rutinas</p>
                      <p className="text-sm text-green-light">Mantén tu racha activa</p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-yellow-light/30 rounded-lg flex items-center justify-center">
                      <span className="text-2xl">👥</span>
                    </div>
                    <div>
                      <p className="font-semibold">Conecta con la comunidad</p>
                      <p className="text-sm text-green-light">Comparte tu experiencia</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Formulario */}
          <div className="bg-white rounded-2xl shadow-2xl p-8">
            <div className="text-center mb-8">
              <div className="flex items-center justify-center space-x-2 mb-4">
                <Heart className="w-10 h-10 text-green-dark" />
                <span className="text-3xl font-bold text-dark">Paso a Paso</span>
              </div>
              <h2 className="text-2xl font-bold text-dark">Bienvenido de nuevo</h2>
              <p className="text-gray-custom mt-2">Inicia sesión para continuar tu progreso</p>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm mb-6 flex items-start">
                <span className="mr-2">⚠️</span>
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="correo" className="block text-sm font-medium text-dark mb-2">
                  Correo electrónico
                </label>
                <div className="relative">
                  <Mail className="w-5 h-5 text-gray-custom absolute left-3 top-1/2 transform -translate-y-1/2" />
                  <input
                    id="correo"
                    name="correo"
                    type="email"
                    required
                    value={formData.correo}
                    onChange={handleChange}
                    placeholder="tu@email.com"
                    className="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-lg focus:border-green-dark focus:outline-none transition-colors"
                  />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <label htmlFor="contrasena" className="block text-sm font-medium text-dark">
                    Contraseña
                  </label>
                  <button type="button" className="text-sm text-green-dark hover:underline">
                    ¿Olvidaste tu contraseña?
                  </button>
                </div>
                <div className="relative">
                  <Lock className="w-5 h-5 text-gray-custom absolute left-3 top-1/2 transform -translate-y-1/2" />
                  <input
                    id="contrasena"
                    name="contrasena"
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={formData.contrasena}
                    onChange={handleChange}
                    placeholder="••••••••"
                    className="w-full pl-12 pr-12 py-3 border-2 border-gray-200 rounded-lg focus:border-green-dark focus:outline-none transition-colors"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-custom hover:text-dark"
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
              </div>

              <div className="flex items-center">
                <input
                  id="remember"
                  type="checkbox"
                  className="w-4 h-4 text-green-dark border-gray-300 rounded focus:ring-green-dark"
                />
                <label htmlFor="remember" className="ml-2 text-sm text-gray-custom">
                  Mantener sesión iniciada
                </label>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-green-dark text-white py-3 rounded-lg font-semibold hover:bg-opacity-90 transition-all shadow-lg hover:shadow-xl flex items-center justify-center disabled:opacity-70 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin mr-2" />
                    Iniciando sesión...
                  </>
                ) : (
                  'Iniciar sesión'
                )}
              </button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-gray-custom text-sm">
                ¿No tienes cuenta?{' '}
                <button onClick={() => navigate('/registro')} className="text-green-dark font-semibold hover:underline">
                  Regístrate gratis
                </button>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
