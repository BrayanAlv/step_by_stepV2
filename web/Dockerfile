# ETAPA 1: Construcción
FROM node:20-alpine as build
WORKDIR /app

# Copiamos package.json y package-lock.json
COPY package*.json ./

# Instalamos dependencias
RUN npm install

# Copiamos el resto del código
COPY . .

# Compilamos el proyecto (Vite generará la carpeta "dist")
RUN npm run build 

# ETAPA 2: Servidor Ligero
FROM nginx:alpine

# Cambia /app/build por /app/dist
COPY --from=build /app/dist /usr/share/nginx/html

# Remplaza la configuración por defecto de Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
