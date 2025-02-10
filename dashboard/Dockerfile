ARG NODE_VERSION=18-alpine

FROM node:$NODE_VERSION AS builder

WORKDIR /src
COPY ["package.json", "package-lock.json*", "./"]
COPY . . 
RUN npm install -g vite
RUN npm install
RUN vite build --base=/news/dashboard


FROM nginx:stable
ARG ENVIRONENT=build
ARG VIEWER
COPY --from=builder /src/${VIEWER}/dist /usr/share/nginx/html/news/dashboard