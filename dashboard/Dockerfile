ARG NODE_VERSION=18-alpine

FROM node:$NODE_VERSION AS builder

WORKDIR /src
COPY ["package.json", "package-lock.json*", "./"]
COPY . . 
RUN npm install -g vite
RUN npm install
RUN vite build --base=/news/dashboard


FROM nginx:stable-alpine

COPY --from=builder /src/dist /usr/share/nginx/html/news/dashboard
COPY vue-router-nginx.conf /etc/nginx/conf.d/default.conf