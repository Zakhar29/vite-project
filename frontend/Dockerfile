FROM node:20-alpine

WORKDIR /app

# Копируем только манифесты (кэшируется отдельно)
COPY package*.json ./

# Устанавливаем зависимости (node_modules не копируется с хоста — см. .dockerignore)
RUN npm config set fetch-timeout 300000 \
    && npm config set fetch-retry-mintimeout 20000 \
    && npm config set fetch-retry-maxtimeout 120000 \
    && npm install

# Копируем исходный код
COPY . .

EXPOSE 5173

# При volume-mount ./frontend:/app зависимости живут в анонимном томе /app/node_modules
CMD ["sh", "-c", "npm install && npm run dev -- --host 0.0.0.0 --port 5173 --strictPort"]