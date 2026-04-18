import React, { useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Heart, Mail, Lock, User, Check, ArrowLeft, Eye, EyeOff, Upload, ArrowRight, CheckCircle2, Loader2, Phone } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const RegistroPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { register } = useAuth();
  const plan = searchParams.get('plan');
  const isPremium = plan === 'premium';

  const [currentStep, setCurrentStep] = useState(1);
  const [showPassword, setShowPassword] = useState(false);
  const [profileImage, setProfileImage] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const [formData, setFormData] = useState({
    nombre: '',
    apellido_paterno: '',
    apellido_materno: '',
    correo: '',
    contrasena: '',
    confirmar_contrasena: '',
    foto_perfil: null,
    acceptTerms: false,
    telefono: '', // Added as API might expect it
  });

  const [errors, setErrors] = useState({});

  const validateStep1 = () => {
    const newErrors = {};

    if (!formData.nombre.trim()) {
      newErrors.nombre = 'El nombre es requerido';
    }
    if (!formData.apellido_paterno.trim()) {
      newErrors.apellido_paterno = 'El apellido paterno es requerido';
    }
    if (!formData.correo.trim()) {
      newErrors.correo = 'El correo es requerido';
    } else if (!/\S+@\S+\.\S+/.test(formData.correo)) {
      newErrors.correo = 'El correo no es válido';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateStep2 = () => {
    const newErrors = {};

    if (!formData.contrasena) {
      newErrors.contrasena = 'La contraseña es requerida';
    } else if (formData.contrasena.length < 8) {
      newErrors.contrasena = 'Mínimo 8 caracteres';
    }

    if (formData.contrasena !== formData.confirmar_contrasena) {
      newErrors.confirmar_contrasena = 'Las contraseñas no coinciden';
    }

    if (!formData.acceptTerms) {
      newErrors.acceptTerms = 'Debes aceptar los términos y condiciones';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNextStep = () => {
    if (currentStep === 1 && validateStep1()) {
      setCurrentStep(2);
    }
  };

  const handlePrevStep = () => {
    setCurrentStep(1);
    setErrors({});
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (validateStep2()) {
      setIsLoading(true);
      setError('');

      const registroData = {
        nombre: formData.nombre,
        apellido_paterno: formData.apellido_paterno,
        apellido_materno: formData.apellido_materno || '',
        correo_electronico: formData.correo,
        contrasena: formData.contrasena,
        telefono: formData.telefono || '0000000000', // Default if required by backend but not in UI
      };

      try {
        await register(registroData);
        navigate('/admin/dashboard');
      } catch (err) {
        setError(err.message || 'Error al registrarse. Intenta de nuevo.');
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
    // Limpiar error del campo cuando el usuario empieza a escribir
    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: ''
      });
    }
    if (error) setError('');
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setProfileImage(reader.result);
        setFormData({
          ...formData,
          foto_perfil: file
        });
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-light/30 to-blue-light/30 relative">
      {/* Botón volver */}
      <button
        onClick={() => navigate('/admin/dashboard')}
        className="absolute top-6 left-6 flex items-center space-x-2 text-dark hover:text-green-dark transition-colors group z-10"
      >
        <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
        <span className="font-medium">Volver al dashboard</span>
      </button>

      <div className="flex items-center justify-center min-h-screen px-4 py-12">
        <div className="grid md:grid-cols-2 gap-8 max-w-5xl w-full items-stretch">
          {/* Imagen ilustrativa */}
          <div className="hidden md:block">
            <div className="bg-gradient-to-br from-blue-dark to-green-dark rounded-3xl p-12 shadow-2xl h-full flex flex-col justify-between">
              <div className="text-white space-y-6">
                <div className="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center mb-8">
                  <Heart className="w-10 h-10 text-white" />
                </div>
                <h3 className="text-4xl font-bold">Empieza tu viaje hoy</h3>
                <p className="text-blue-light text-lg leading-relaxed">
                  Únete a miles de personas que ya están construyendo hábitos saludables con Paso a Paso.
                </p>

                <div className="space-y-4 pt-6">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-green-light/30 rounded-lg flex items-center justify-center">
                      <span className="text-2xl">🎯</span>
                    </div>
                    <div>
                      <p className="font-semibold">Crea tus rutinas</p>
                      <p className="text-sm text-blue-light">Personaliza según tus metas</p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-yellow-light/30 rounded-lg flex items-center justify-center">
                      <span className="text-2xl">📅</span>
                    </div>
                    <div>
                      <p className="font-semibold">Planifica tu semana</p>
                      <p className="text-sm text-blue-light">Organiza tu tiempo fácilmente</p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-red-light/30 rounded-lg flex items-center justify-center">
                      <span className="text-2xl">🚀</span>
                    </div>
                    <div>
                      <p className="font-semibold">Alcanza tus objetivos</p>
                      <p className="text-sm text-blue-light">A tu ritmo, sin presión</p>
                    </div>
                  </div>
                </div>
              </div>

              {isPremium && (
                <div className="mt-8 bg-yellow/20 border-2 border-yellow rounded-xl p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="text-2xl">✨</span>
                    <p className="font-bold text-white">Plan Premium</p>
                  </div>
                  <p className="text-sm text-yellow-light">
                    14 días gratis + todas las funciones premium
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Formulario */}
          <div className="bg-white rounded-3xl shadow-2xl p-8 flex flex-col">
            <div className="text-center mb-6">
              <div className="flex items-center justify-center space-x-2 mb-4">
                <Heart className="w-10 h-10 text-green-dark" />
                <span className="text-3xl font-bold text-dark">Paso a Paso</span>
              </div>
              <h2 className="text-2xl font-bold text-dark">Crea tu cuenta</h2>
              <p className="text-gray-custom mt-2">
                {isPremium ? '✨ 14 días de prueba gratis incluidos' : 'Comienza gratis hoy mismo'}
              </p>
            </div>

            {/* Progress indicator */}
            <div className="flex items-center justify-center mb-6">
              <div className="flex items-center space-x-2">
                <div className={`flex items-center justify-center w-8 h-8 rounded-full ${currentStep >= 1 ? 'bg-green-dark text-white' : 'bg-gray-200 text-gray-custom'}`}>
                  {currentStep > 1 ? <CheckCircle2 className="w-5 h-5" /> : '1'}
                </div>
                <div className={`h-1 w-12 ${currentStep >= 2 ? 'bg-green-dark' : 'bg-gray-200'}`}></div>
                <div className={`flex items-center justify-center w-8 h-8 rounded-full ${currentStep >= 2 ? 'bg-green-dark text-white' : 'bg-gray-200 text-gray-custom'}`}>
                  2
                </div>
              </div>
            </div>

            {isPremium && (
              <div className="bg-gradient-to-r from-green-dark to-blue-dark text-white rounded-lg p-4 mb-6">
                <div className="flex items-center space-x-2 mb-2">
                  <Check className="w-5 h-5" />
                  <span className="font-semibold">Plan Premium seleccionado</span>
                </div>
                <p className="text-sm text-green-light">
                  Disfruta de todas las funciones premium por 14 días. Sin tarjeta de crédito.
                </p>
              </div>
            )}

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm mb-4">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5 flex-1 flex flex-col">
              {/* Paso 1: Información Personal */}
              {currentStep === 1 && (
                <div className="space-y-5 flex-1">
                  <div>
                    <label htmlFor="nombre" className="block text-sm font-medium text-dark mb-2">
                      Nombre <span className="text-red-dark">*</span>
                    </label>
                    <div className="relative">
                      <User className="w-5 h-5 text-gray-custom absolute left-3 top-1/2 transform -translate-y-1/2" />
                      <input
                        id="nombre"
                        name="nombre"
                        type="text"
                        value={formData.nombre}
                        onChange={handleChange}
                        placeholder="Ej: Juan"
                        className={`w-full pl-12 pr-4 py-3 border-2 ${errors.nombre ? 'border-red-dark' : 'border-gray-200'} rounded-lg focus:border-green-dark focus:outline-none transition-colors`}
                      />
                    </div>
                    {errors.nombre && <p className="text-red-dark text-xs mt-1">{errors.nombre}</p>}
                  </div>

                  <div>
                    <label htmlFor="apellido_paterno" className="block text-sm font-medium text-dark mb-2">
                      Apellido Paterno <span className="text-red-dark">*</span>
                    </label>
                    <div className="relative">
                      <User className="w-5 h-5 text-gray-custom absolute left-3 top-1/2 transform -translate-y-1/2" />
                      <input
                        id="apellido_paterno"
                        name="apellido_paterno"
                        type="text"
                        value={formData.apellido_paterno}
                        onChange={handleChange}
                        placeholder="Ej: Pérez"
                        className={`w-full pl-12 pr-4 py-3 border-2 ${errors.apellido_paterno ? 'border-red-dark' : 'border-gray-200'} rounded-lg focus:border-green-dark focus:outline-none transition-colors`}
                      />
                    </div>
                    {errors.apellido_paterno && <p className="text-red-dark text-xs mt-1">{errors.apellido_paterno}</p>}
                  </div>

                  <div>
                    <label htmlFor="apellido_materno" className="block text-sm font-medium text-dark mb-2">
                      Apellido Materno
                    </label>
                    <div className="relative">
                      <User className="w-5 h-5 text-gray-custom absolute left-3 top-1/2 transform -translate-y-1/2" />
                      <input
                        id="apellido_materno"
                        name="apellido_materno"
                        type="text"
                        value={formData.apellido_materno}
                        onChange={handleChange}
                        placeholder="Ej: García (opcional)"
                        className="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-lg focus:border-green-dark focus:outline-none transition-colors"
                      />
                    </div>
                  </div>

                  <div>
                    <label htmlFor="correo" className="block text-sm font-medium text-dark mb-2">
                      Correo electrónico <span className="text-red-dark">*</span>
                    </label>
                    <div className="relative">
                      <Mail className="w-5 h-5 text-gray-custom absolute left-3 top-1/2 transform -translate-y-1/2" />
                      <input
                        id="correo"
                        name="correo"
                        type="email"
                        value={formData.correo}
                        onChange={handleChange}
                        placeholder="tu@email.com"
                        className={`w-full pl-12 pr-4 py-3 border-2 ${errors.correo ? 'border-red-dark' : 'border-gray-200'} rounded-lg focus:border-green-dark focus:outline-none transition-colors`}
                      />
                    </div>
                    {errors.correo && <p className="text-red-dark text-xs mt-1">{errors.correo}</p>}
                  </div>

                  <div>
                    <label htmlFor="telefono" className="block text-sm font-medium text-dark mb-2">
                      Teléfono <span className="text-red-dark">*</span>
                    </label>
                    <div className="relative">
                      <Phone className="w-5 h-5 text-gray-custom absolute left-3 top-1/2 transform -translate-y-1/2" />
                      <input
                        id="telefono"
                        name="telefono"
                        type="text"
                        value={formData.telefono}
                        onChange={handleChange}
                        placeholder="1234567890"
                        className={`w-full pl-12 pr-4 py-3 border-2 ${errors.telefono ? 'border-red-dark' : 'border-gray-200'} rounded-lg focus:border-green-dark focus:outline-none transition-colors`}
                      />
                    </div>
                    {errors.telefono && <p className="text-red-dark text-xs mt-1">{errors.telefono}</p>}
                  </div>
                  <button
                    type="button"
                    onClick={handleNextStep}
                    className="w-full bg-green-dark text-white py-3 rounded-lg font-semibold hover:bg-opacity-90 transition-all shadow-lg hover:shadow-xl flex items-center justify-center space-x-2 mt-auto"
                  >
                    <span>Continuar</span>
                    <ArrowRight className="w-5 h-5" />
                  </button>
                </div>
              )}

              {/* Paso 2: Contraseña y Foto */}
              {currentStep === 2 && (
                <div className="space-y-5 flex-1">
                  {/* Foto de perfil (oculta temporalmente según solicitud) */}
                  <div className="hidden flex-col items-center">
                    <div className="relative">
                      <div className="w-24 h-24 rounded-full bg-neutral-bg border-2 border-gray-200 flex items-center justify-center overflow-hidden">
                        {profileImage ? (
                          <img src={profileImage} alt="Profile" className="w-full h-full object-cover" />
                        ) : (
                          <User className="w-12 h-12 text-gray-custom" />
                        )}
                      </div>
                      <label className="absolute bottom-0 right-0 bg-green-dark text-white p-2 rounded-full cursor-pointer hover:bg-opacity-90 transition-all shadow-lg">
                        <Upload className="w-4 h-4" />
                        <input
                          type="file"
                          accept="image/*"
                          onChange={handleImageChange}
                          className="hidden"
                        />
                      </label>
                    </div>
                    <p className="text-xs text-gray-custom mt-2">Foto de perfil (opcional)</p>
                  </div>

                  <div>
                    <label htmlFor="contrasena" className="block text-sm font-medium text-dark mb-2">
                      Contraseña <span className="text-red-dark">*</span>
                    </label>
                    <div className="relative">
                      <Lock className="w-5 h-5 text-gray-custom absolute left-3 top-1/2 transform -translate-y-1/2" />
                      <input
                        id="contrasena"
                        name="contrasena"
                        type={showPassword ? 'text' : 'password'}
                        value={formData.contrasena}
                        onChange={handleChange}
                        placeholder="••••••••"
                        className={`w-full pl-12 pr-12 py-3 border-2 ${errors.contrasena ? 'border-red-dark' : 'border-gray-200'} rounded-lg focus:border-green-dark focus:outline-none transition-colors`}
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-custom hover:text-dark"
                      >
                        {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                      </button>
                    </div>
                    {errors.contrasena ? (
                      <p className="text-red-dark text-xs mt-1">{errors.contrasena}</p>
                    ) : (
                      <p className="text-xs text-gray-custom mt-1">Mínimo 8 caracteres</p>
                    )}
                  </div>

                  <div>
                    <label htmlFor="confirmar_contrasena" className="block text-sm font-medium text-dark mb-2">
                      Confirmar Contraseña <span className="text-red-dark">*</span>
                    </label>
                    <div className="relative">
                      <Lock className="w-5 h-5 text-gray-custom absolute left-3 top-1/2 transform -translate-y-1/2" />
                      <input
                        id="confirmar_contrasena"
                        name="confirmar_contrasena"
                        type={showPassword ? 'text' : 'password'}
                        value={formData.confirmar_contrasena}
                        onChange={handleChange}
                        placeholder="••••••••"
                        className={`w-full pl-12 pr-4 py-3 border-2 ${errors.confirmar_contrasena ? 'border-red-dark' : 'border-gray-200'} rounded-lg focus:border-green-dark focus:outline-none transition-colors`}
                      />
                    </div>
                    {errors.confirmar_contrasena && <p className="text-red-dark text-xs mt-1">{errors.confirmar_contrasena}</p>}
                  </div>

                  <div className="flex items-start space-x-3">
                    <input
                      type="checkbox"
                      id="acceptTerms"
                      name="acceptTerms"
                      checked={formData.acceptTerms}
                      onChange={handleChange}
                      className="w-5 h-5 text-green-dark border-gray-300 rounded focus:ring-green-dark mt-0.5"
                    />
                    <label htmlFor="acceptTerms" className="text-sm text-gray-custom">
                      Acepto los{' '}
                      <a href="#" className="text-green-dark hover:underline">
                        términos y condiciones
                      </a>{' '}
                      y la{' '}
                      <a href="#" className="text-green-dark hover:underline">
                        política de privacidad
                      </a>
                    </label>
                  </div>
                  {errors.acceptTerms && <p className="text-red-dark text-xs">{errors.acceptTerms}</p>}

                  <div className="flex space-x-3 mt-auto">
                    <button
                      type="button"
                      onClick={handlePrevStep}
                      className="flex-1 bg-white border-2 border-green-dark text-green-dark py-3 rounded-lg font-semibold hover:bg-green-light/30 transition-all flex items-center justify-center space-x-2"
                    >
                      <ArrowLeft className="w-5 h-5" />
                      <span>Atrás</span>
                    </button>
                    <button
                      type="submit"
                      disabled={isLoading}
                      className="flex-1 bg-green-dark text-white py-3 rounded-lg font-semibold hover:bg-opacity-90 transition-all shadow-lg hover:shadow-xl flex items-center justify-center disabled:opacity-70 disabled:cursor-not-allowed"
                    >
                      {isLoading ? (
                        <>
                          <Loader2 className="w-5 h-5 animate-spin mr-2" />
                          Procesando...
                        </>
                      ) : (
                        isPremium ? 'Comenzar prueba gratis' : 'Crear cuenta'
                      )}
                    </button>
                  </div>
                </div>
              )}
            </form>

            <div className="mt-6 text-center">
              <p className="text-gray-custom text-sm">
                ¿Ya tienes cuenta?{' '}
                <button onClick={() => navigate('/login')} className="text-green-dark font-semibold hover:underline">
                  Inicia sesión
                </button>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegistroPage;
