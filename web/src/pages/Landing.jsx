import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Calendar, Heart, Users, CheckCircle2, Smartphone, Sparkles, TrendingUp, Shield, Zap, Menu, X, ArrowRight, Check, Star } from 'lucide-react';

const LandingPage = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-neutral-light">
      {/* Navbar */}
      <nav className="fixed w-full bg-white/95 backdrop-blur-sm shadow-sm z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <Heart className="w-8 h-8 text-green-dark" />
              <span className="text-2xl font-bold text-dark">Paso a Paso</span>
            </div>

            {/* Desktop Menu */}
            <div className="hidden md:flex items-center space-x-8">
              <a href="#como-funciona" className="text-gray-custom hover:text-green-dark transition-colors">Cómo funciona</a>
              <a href="#beneficios" className="text-gray-custom hover:text-green-dark transition-colors">Beneficios</a>
              <a href="#app" className="text-gray-custom hover:text-green-dark transition-colors">App móvil</a>
              <a href="#planes" className="text-gray-custom hover:text-green-dark transition-colors">Planes</a>
              <Link to="/login" className="text-gray-custom hover:text-green-dark transition-colors">Iniciar sesión</Link>
              {/* <Link 
                to="/registro" 
                className="bg-green-dark text-white px-6 py-2 rounded-full hover:bg-opacity-90 transition-all shadow-md hover:shadow-lg"
              >
                Empieza gratis
              </Link> */}
            </div>

            {/* Mobile menu button */}
            <button
              className="md:hidden text-dark"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-white border-t border-gray-200">
            <div className="px-4 py-4 space-y-3">
              <a href="#como-funciona" className="block text-gray-custom hover:text-green-dark">Cómo funciona</a>
              <a href="#beneficios" className="block text-gray-custom hover:text-green-dark">Beneficios</a>
              <a href="#app" className="block text-gray-custom hover:text-green-dark">App móvil</a>
              <a href="#planes" className="block text-gray-custom hover:text-green-dark">Planes</a>
              <Link to="/login" className="block text-gray-custom hover:text-green-dark">Iniciar sesión</Link>
              {/* <Link to="/registro" className="block bg-green-dark text-white px-6 py-2 rounded-full text-center">
                Empieza gratis
              </Link> */}
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-green-light/30 via-blue-light/20 to-neutral-light">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="space-y-6">
              <div className="inline-flex items-center space-x-2 bg-green-light/50 px-4 py-2 rounded-full">
                <Sparkles className="w-5 h-5 text-green-dark" />
                <span className="text-sm font-medium text-dark">Construye hábitos sin presión</span>
              </div>

              <h1 className="text-5xl md:text-6xl font-bold text-dark leading-tight">
                Tu bienestar,
                <span className="text-green-dark"> a tu ritmo</span>
              </h1>

              <p className="text-xl text-gray-custom leading-relaxed">
                Paso a Paso te ayuda a crear rutinas saludables de forma gradual y sostenible.
                Sin presión, sin estrés. Solo tú, tus metas y un acompañamiento empático cada día.
              </p>

              <p className="text-xl text-gray-custom leading-relaxed">
                “Crea tu cuenta en la web y vive la experiencia completa en nuestra app móvil.”
              </p>

              <div className="flex flex-col sm:flex-row gap-4 pt-4">
                {/* <Link
                  to="/registro"
                  className="bg-green-dark text-white px-8 py-4 rounded-full font-semibold hover:bg-opacity-90 transition-all shadow-lg hover:shadow-xl flex items-center justify-center space-x-2 group"
                >
                  <span>Empieza gratis</span>
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </Link> */}

                <a
                  href="#planes"
                  className="bg-white text-green-dark border-2 border-green-dark px-8 py-4 rounded-full font-semibold hover:bg-green-light/30 transition-all flex items-center justify-center"
                >
                  Prueba 14 días gratis
                </a>
              </div>

              <div className="flex items-center space-x-6 pt-4">
                <div className="flex items-center space-x-2">
                  <CheckCircle2 className="w-5 h-5 text-green-dark" />
                  <span className="text-sm text-gray-custom">Sin tarjeta de crédito</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle2 className="w-5 h-5 text-green-dark" />
                  <span className="text-sm text-gray-custom">Cancela cuando quieras</span>
                </div>
              </div>
            </div>

            <div className="relative">
              <div className="bg-gradient-to-br from-green-dark to-blue-dark rounded-3xl p-8 shadow-2xl transform rotate-3 hover:rotate-0 transition-transform duration-300">
                <div className="bg-white rounded-2xl p-6 space-y-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-green-light rounded-full flex items-center justify-center">
                      <Heart className="w-6 h-6 text-green-dark" />
                    </div>
                    <div>
                      <p className="font-semibold text-dark">Tu rutina de hoy</p>
                      <p className="text-sm text-gray-custom">3 de 5 completadas</p>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center space-x-3 bg-green-light/30 p-3 rounded-lg">
                      <CheckCircle2 className="w-5 h-5 text-green-dark" />
                      <span className="text-dark">Meditación matutina</span>
                    </div>
                    <div className="flex items-center space-x-3 bg-green-light/30 p-3 rounded-lg">
                      <CheckCircle2 className="w-5 h-5 text-green-dark" />
                      <span className="text-dark">Caminar 15 minutos</span>
                    </div>
                    <div className="flex items-center space-x-3 bg-blue-light/30 p-3 rounded-lg">
                      <Calendar className="w-5 h-5 text-blue-dark" />
                      <span className="text-dark">Leer antes de dormir</span>
                    </div>
                  </div>

                  <div className="pt-4">
                    <div className="w-full bg-neutral-bg rounded-full h-3">
                      <div className="bg-green-dark h-3 rounded-full" style={{ width: '60%' }}></div>
                    </div>
                    <p className="text-sm text-gray-custom mt-2 text-center">¡Vas muy bien! 60% completado</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Cómo funciona */}
      <section id="como-funciona" className="py-20 px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-dark mb-4">
              Cómo funciona
            </h2>
            <p className="text-xl text-gray-custom max-w-2xl mx-auto">
              Un sistema simple y efectivo para construir hábitos duraderos
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-8">
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-green-light rounded-2xl flex items-center justify-center mx-auto">
                <Sparkles className="w-8 h-8 text-green-dark" />
              </div>
              <h3 className="text-xl font-bold text-dark">1. Crea tus rutinas</h3>
              <p className="text-gray-custom">
                Define rutinas semanales que se adapten a tu estilo de vida y objetivos personales
              </p>
            </div>

            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-blue-light rounded-2xl flex items-center justify-center mx-auto">
                <Calendar className="w-8 h-8 text-blue-dark" />
              </div>
              <h3 className="text-xl font-bold text-dark">2. Planifica</h3>
              <p className="text-gray-custom">
                Organiza tus rutinas en un calendario visual y flexible que puedes ajustar cuando quieras
              </p>
            </div>

            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-yellow-light rounded-2xl flex items-center justify-center mx-auto">
                <Heart className="w-8 h-8 text-yellow" />
              </div>
              <h3 className="text-xl font-bold text-dark">3. Acompañamiento</h3>
              <p className="text-gray-custom">
                Recibe recordatorios amables y motivación diaria para mantener tu progreso
              </p>
            </div>

            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-red-light rounded-2xl flex items-center justify-center mx-auto">
                <Users className="w-8 h-8 text-red-dark" />
              </div>
              <h3 className="text-xl font-bold text-dark">4. Comunidad</h3>
              <p className="text-gray-custom">
                Comparte tu experiencia y aprende de otros en una comunidad de apoyo
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Beneficios */}
      <section id="beneficios" className="py-20 px-4 sm:px-6 lg:px-8 bg-neutral-bg">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-dark mb-4">
              ¿Por qué Paso a Paso?
            </h2>
            <p className="text-xl text-gray-custom max-w-2xl mx-auto">
              Un enfoque diferente para construir hábitos sostenibles
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-shadow">
              <div className="w-14 h-14 bg-green-light rounded-xl flex items-center justify-center mb-4">
                <Shield className="w-7 h-7 text-green-dark" />
              </div>
              <h3 className="text-2xl font-bold text-dark mb-3">Sin presión diaria</h3>
              <p className="text-gray-custom leading-relaxed">
                No hay metas imposibles ni streaks estresantes. Construye hábitos a tu ritmo,
                sin culpa si necesitas un día de descanso.
              </p>
            </div>

            <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-shadow">
              <div className="w-14 h-14 bg-blue-light rounded-xl flex items-center justify-center mb-4">
                <Heart className="w-7 h-7 text-blue-dark" />
              </div>
              <h3 className="text-2xl font-bold text-dark mb-3">Enfoque emocional</h3>
              <p className="text-gray-custom leading-relaxed">
                Priorizamos tu bienestar emocional. Cada paso cuenta y celebramos tus avances,
                por pequeños que sean.
              </p>
            </div>

            <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-shadow">
              <div className="w-14 h-14 bg-yellow-light rounded-xl flex items-center justify-center mb-4">
                <TrendingUp className="w-7 h-7 text-yellow" />
              </div>
              <h3 className="text-2xl font-bold text-dark mb-3">Progreso gradual</h3>
              <p className="text-gray-custom leading-relaxed">
                Los cambios duraderos toman tiempo. Visualiza tu evolución y celebra
                cada logro en tu camino hacia una vida más saludable.
              </p>
            </div>

            <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-shadow">
              <div className="w-14 h-14 bg-red-light rounded-xl flex items-center justify-center mb-4">
                <Zap className="w-7 h-7 text-red-dark" />
              </div>
              <h3 className="text-2xl font-bold text-dark mb-3">Totalmente personalizable</h3>
              <p className="text-gray-custom leading-relaxed">
                Crea rutinas únicas para ti. Ajusta horarios, frecuencia y recordatorios
                según tus necesidades y preferencias.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* App Móvil */}
      <section id="app" className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-blue-light/20 to-green-light/20">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="space-y-6">
              <h2 className="text-4xl md:text-5xl font-bold text-dark">
                Tu bienestar en tu bolsillo
              </h2>
              <p className="text-xl text-gray-custom leading-relaxed">
                Lleva Paso a Paso contigo a todas partes. Gestiona tus rutinas,
                recibe recordatorios y sigue tu progreso desde cualquier lugar.
              </p>

              <div className="space-y-4">
                <div className="flex items-start space-x-4">
                  <div className="w-10 h-10 bg-green-light rounded-lg flex items-center justify-center flex-shrink-0">
                    <CheckCircle2 className="w-6 h-6 text-green-dark" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-dark mb-1">Marca tus rutinas completadas</h4>
                    <p className="text-gray-custom">Un simple tap para registrar tus logros diarios</p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="w-10 h-10 bg-blue-light rounded-lg flex items-center justify-center flex-shrink-0">
                    <Calendar className="w-6 h-6 text-blue-dark" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-dark mb-1">Vista de calendario intuitiva</h4>
                    <p className="text-gray-custom">Visualiza tu semana y planifica con facilidad</p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="w-10 h-10 bg-yellow-light rounded-lg flex items-center justify-center flex-shrink-0">
                    <Sparkles className="w-6 h-6 text-yellow" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-dark mb-1">Notificaciones personalizadas</h4>
                    <p className="text-gray-custom">Recordatorios amables en el momento perfecto</p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="w-10 h-10 bg-red-light rounded-lg flex items-center justify-center flex-shrink-0">
                    <TrendingUp className="w-6 h-6 text-red-dark" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-dark mb-1">Seguimiento de progreso</h4>
                    <p className="text-gray-custom">Estadísticas motivadoras de tu evolución</p>
                  </div>
                </div>
              </div>

              <div className="pt-4">
                <button className="bg-dark text-white px-8 py-4 rounded-full font-semibold hover:bg-opacity-90 transition-all shadow-lg hover:shadow-xl flex items-center space-x-2">
                  <Smartphone className="w-5 h-5" />
                  <span>Descargar app</span>
                </button>
                <p className="text-sm text-gray-custom mt-3">Disponible para iOS y Android</p>
              </div>
            </div>

            <div className="relative">
              <div className="relative mx-auto w-64 h-[500px] bg-dark rounded-[3rem] p-3 shadow-2xl">
                <div className="w-full h-full bg-white rounded-[2.5rem] overflow-hidden">
                  <div className="h-full bg-gradient-to-b from-green-light/40 to-blue-light/40 p-6">
                    <div className="text-center mb-6">
                      <p className="text-sm text-gray-custom">Hoy, 15 Ene</p>
                      <h3 className="text-2xl font-bold text-dark mt-2">¡Buenos días! 👋</h3>
                    </div>

                    <div className="space-y-3">
                      <div className="bg-white rounded-xl p-4 shadow-md">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-semibold text-dark">Rutina matutina</span>
                          <CheckCircle2 className="w-6 h-6 text-green-dark" />
                        </div>
                        <div className="flex items-center space-x-2 text-sm text-gray-custom">
                          <Calendar className="w-4 h-4" />
                          <span>7:00 AM</span>
                        </div>
                      </div>

                      <div className="bg-white rounded-xl p-4 shadow-md">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-semibold text-dark">Ejercicio</span>
                          <div className="w-6 h-6 border-2 border-gray-custom rounded-full"></div>
                        </div>
                        <div className="flex items-center space-x-2 text-sm text-gray-custom">
                          <Calendar className="w-4 h-4" />
                          <span>6:00 PM</span>
                        </div>
                      </div>

                      <div className="bg-white rounded-xl p-4 shadow-md">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-semibold text-dark">Lectura nocturna</span>
                          <div className="w-6 h-6 border-2 border-gray-custom rounded-full"></div>
                        </div>
                        <div className="flex items-center space-x-2 text-sm text-gray-custom">
                          <Calendar className="w-4 h-4" />
                          <span>9:00 PM</span>
                        </div>
                      </div>
                    </div>

                    <div className="mt-6 bg-white rounded-xl p-4 shadow-md">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-sm font-semibold text-dark">Progreso semanal</span>
                        <span className="text-sm text-green-dark font-bold">65%</span>
                      </div>
                      <div className="w-full bg-neutral-bg rounded-full h-2">
                        <div className="bg-green-dark h-2 rounded-full" style={{ width: '65%' }}></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Planes */}
      <section id="planes" className="py-20 px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-dark mb-4">
              Elige tu plan
            </h2>
            <p className="text-xl text-gray-custom max-w-2xl mx-auto">
              Comienza gratis y actualiza cuando estés listo. Sin compromisos.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
            {/* Plan Free */}
            <div className="bg-neutral-bg rounded-2xl p-8 border-2 border-transparent hover:border-green-dark transition-all">
              <div className="text-center mb-6">
                <h3 className="text-2xl font-bold text-dark mb-2">Free</h3>
                <div className="text-5xl font-bold text-dark mb-2">$0</div>
                <p className="text-gray-custom">Para siempre</p>
              </div>

              <ul className="space-y-4 mb-8">
                <li className="flex items-start space-x-3">
                  <Check className="w-6 h-6 text-green-dark flex-shrink-0 mt-0.5" />
                  <span className="text-gray-custom">Hasta 3 rutinas activas</span>
                </li>
                <li className="flex items-start space-x-3">
                  <Check className="w-6 h-6 text-green-dark flex-shrink-0 mt-0.5" />
                  <span className="text-gray-custom">Calendario semanal</span>
                </li>
                <li className="flex items-start space-x-3">
                  <Check className="w-6 h-6 text-green-dark flex-shrink-0 mt-0.5" />
                  <span className="text-gray-custom">Seguimiento básico de progreso</span>
                </li>
                <li className="flex items-start space-x-3">
                  <Check className="w-6 h-6 text-green-dark flex-shrink-0 mt-0.5" />
                  <span className="text-gray-custom">App móvil</span>
                </li>
                <li className="flex items-start space-x-3">
                  <Check className="w-6 h-6 text-green-dark flex-shrink-0 mt-0.5" />
                  <span className="text-gray-custom">Comunidad de apoyo</span>
                </li>
              </ul>

              {/* <Link
                to="/registro"
                className="block w-full bg-white border-2 border-green-dark text-green-dark px-6 py-3 rounded-full font-semibold hover:bg-green-light/30 transition-all text-center"
              >
                Comenzar gratis
              </Link> */}
            </div>

            {/* Plan Premium */}
            <div className="bg-gradient-to-br from-green-dark to-blue-dark rounded-2xl p-8 text-white relative overflow-hidden shadow-2xl">
              <div className="absolute top-4 right-4 bg-yellow text-dark px-4 py-1 rounded-full text-sm font-bold">
                Popular
              </div>

              <div className="text-center mb-6 relative z-10">
                <h3 className="text-2xl font-bold mb-2">Premium</h3>
                <div className="text-5xl font-bold mb-2">$9.99</div>
                <p className="text-green-light">por mes</p>
                <p className="text-sm text-green-light mt-2">✨ 14 días de prueba gratis</p>
              </div>

              <ul className="space-y-4 mb-8 relative z-10">
                <li className="flex items-start space-x-3">
                  <Check className="w-6 h-6 text-yellow flex-shrink-0 mt-0.5" />
                  <span className="text-white font-medium">Rutinas ilimitadas</span>
                </li>
                <li className="flex items-start space-x-3">
                  <Check className="w-6 h-6 text-yellow flex-shrink-0 mt-0.5" />
                  <span className="text-white font-medium">Calendario mensual y anual</span>
                </li>
                <li className="flex items-start space-x-3">
                  <Check className="w-6 h-6 text-yellow flex-shrink-0 mt-0.5" />
                  <span className="text-white font-medium">Estadísticas avanzadas</span>
                </li>
                <li className="flex items-start space-x-3">
                  <Check className="w-6 h-6 text-yellow flex-shrink-0 mt-0.5" />
                  <span className="text-white font-medium">Recordatorios personalizados</span>
                </li>
                <li className="flex items-start space-x-3">
                  <Check className="w-6 h-6 text-yellow flex-shrink-0 mt-0.5" />
                  <span className="text-white font-medium">Exportar datos y reportes</span>
                </li>
                <li className="flex items-start space-x-3">
                  <Check className="w-6 h-6 text-yellow flex-shrink-0 mt-0.5" />
                  <span className="text-white font-medium">Soporte prioritario</span>
                </li>
                <li className="flex items-start space-x-3">
                  <Check className="w-6 h-6 text-yellow flex-shrink-0 mt-0.5" />
                  <span className="text-white font-medium">Acceso anticipado a nuevas funciones</span>
                </li>
              </ul>

              <Link
                to="/registro?plan=premium"
                className="block w-full bg-yellow text-dark px-6 py-3 rounded-full font-bold hover:bg-opacity-90 transition-all text-center relative z-10 shadow-lg"
              >
                Probar 14 días gratis
              </Link>

              <div className="absolute -bottom-20 -right-20 w-64 h-64 bg-white/10 rounded-full blur-3xl"></div>
              <div className="absolute -top-20 -left-20 w-64 h-64 bg-white/10 rounded-full blur-3xl"></div>
            </div>
          </div>

          <p className="text-center text-gray-custom mt-8 text-sm">
            💳 Sin tarjeta de crédito requerida para la prueba gratuita • Cancela en cualquier momento
          </p>
        </div>
      </section>

      {/* CTA Final */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-green-dark via-blue-dark to-green-dark">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Comienza tu viaje hoy
          </h2>
          <p className="text-xl text-green-light mb-8 leading-relaxed">
            Miles de personas ya están construyendo hábitos saludables con Paso a Paso.
            Es tu turno de dar el primer paso hacia una vida más equilibrada.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-8">
            {/* <Link
              to="/registro"
              className="bg-yellow text-dark px-10 py-4 rounded-full font-bold hover:bg-opacity-90 transition-all shadow-lg hover:shadow-xl flex items-center space-x-2 text-lg"
            >
              <span>Crear cuenta gratis</span>
              <ArrowRight className="w-5 h-5" />
            </Link> */}

            <a
              href="#planes"
              className="bg-white/20 backdrop-blur-sm text-white border-2 border-white px-10 py-4 rounded-full font-bold hover:bg-white/30 transition-all text-lg"
            >
              Ver planes
            </a>
          </div>

          <div className="flex items-center justify-center space-x-8 text-green-light">
            <div className="flex items-center space-x-2">
              <Star className="w-5 h-5 fill-yellow text-yellow" />
              <span className="text-sm">4.8/5 en las tiendas</span>
            </div>
            <div className="flex items-center space-x-2">
              <Users className="w-5 h-5" />
              <span className="text-sm">+10,000 usuarios activos</span>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-dark text-white py-8 px-2 sm:px-4 lg:px-6">
        <div className="border-t border-gray-custom/30 pt-4 text-center text-sm text-gray-custom">
          <p>© 2026 Paso a Paso. Todos los derechos reservados.</p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;