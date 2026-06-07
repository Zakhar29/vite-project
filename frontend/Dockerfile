FROM node:20-alpine

WORKDIR /app

# Копируем только манифесты (кэшируется отдельно)
COPY package*.json ./

# Устанавливаем зависимости ЛОКАЛЬНО
RUN npm install

# Копируем исходный код
COPY . .

# Открываем порт
EXPOSE 5173

# Запускаем dev-сервер
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173", "--strictPort"]