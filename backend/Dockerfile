# Usamos una versión ligera de Python para ahorrar espacio
FROM python:3.10-slim

# Le decimos a Docker que trabaje en la carpeta /app
WORKDIR /app

# Copiamos el archivo de requerimientos primero (para optimizar caché)
COPY requirements.txt .

# Instalamos las librerías
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el resto del código del backend
COPY . .

# Exponemos el puerto 8000
EXPOSE 8000

# Comando para iniciar FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
