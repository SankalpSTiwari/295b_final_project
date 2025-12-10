# Build React app
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
# Allow overriding API URLs at build time
ARG REACT_APP_API_URL
ARG REACT_APP_FLASK_URL
ENV REACT_APP_API_URL=${REACT_APP_API_URL}
ENV REACT_APP_FLASK_URL=${REACT_APP_FLASK_URL}
RUN npm run build

# Serve with nginx
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]

