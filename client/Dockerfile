FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm cache clean --force
RUN npm ci --no-audit --no-fund
COPY . .

# Accept build-time environment variable for Vite
ARG VITE_SERVER_URL
ENV VITE_SERVER_URL=$VITE_SERVER_URL

RUN npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html

RUN printf 'server { listen 8080; root /usr/share/nginx/html; index index.html; location / { try_files $uri /index.html; } }' > /etc/nginx/conf.d/default.conf
EXPOSE 8080
CMD ["nginx","-g","daemon off;"]

# Create nginx config that uses Railway's PORT environment variable
# RUN printf 'server { \
#     listen $PORT; \
#     root /usr/share/nginx/html; \
#     index index.html; \
#     location / { \
#         try_files $uri /index.html; \
#     } \
#     location /api { \
#         proxy_pass $VITE_SERVER_URL; \
#         proxy_set_header Host $host; \
#         proxy_set_header X-Real-IP $remote_addr; \
#         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
#         proxy_set_header X-Forwarded-Proto $scheme; \
#     } \
# }' > /etc/nginx/conf.d/default.conf

# Use envsubst to substitute environment variables at runtime
# CMD ["sh", "-c", "envsubst '${PORT} ${VITE_SERVER_URL}' < /etc/nginx/conf.d/default.conf > /etc/nginx/conf.d/default.conf.tmp && mv /etc/nginx/conf.d/default.conf.tmp /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]

