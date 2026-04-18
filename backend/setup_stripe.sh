#!/bin/bash

# ============================================
# Script de Configuración - Sistema de Pagos
# ============================================
# Instala y configura la integración con Stripe

echo "🚀 Iniciando configuración del sistema de pagos con Stripe..."

# 1. Activar venv
echo "📦 Activando entorno virtual..."
. venv/bin/activate

# 2. Instalar stripe
echo "📥 Instalando librería stripe..."
pip install stripe

# 3. Actualizar requirements.txt
echo "📝 Verificando requirements.txt..."
if grep -q "stripe" requirements.txt; then
    echo "✓ stripe ya está en requirements.txt"
else
    echo "stripe==11.1.3" >> requirements.txt
    echo "✓ stripe agregado a requirements.txt"
fi

# 4. Crear .env si no existe
if [ ! -f .env ]; then
    echo "📄 Creando archivo .env..."
    cp .env.example .env
    echo "⚠️  IMPORTANTE: Edita .env y agrega tus claves de Stripe"
else
    echo "✓ .env ya existe"
fi

# 5. Verificar migraciones
echo "🗄️  Para aplicar migraciones a la BD, ejecuta:"
echo "   mysql -u root -p rutinas_test < migrations/01_add_stripe_fields.sql"

# 6. Verificar importaciones
echo "🔍 Verificando importaciones..."
python -c "from app.api.v1 import pagos; print('✓ Router de pagos importado correctamente')" && \
python -c "from app.services import pago_service; print('✓ Servicio de pagos importado correctamente')" || \
echo "❌ Error en importaciones"

echo ""
echo "✅ Configuración completada!"
echo ""
echo "Próximos pasos:"
echo "1. Edita .env con tus claves de Stripe"
echo "2. Ejecuta la migración SQL"
echo "3. Inicia el servidor: uvicorn app.main:app --reload"
echo "4. Prueba en: http://localhost:8000/docs"
echo ""

