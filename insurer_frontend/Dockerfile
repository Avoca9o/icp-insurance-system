FROM node:18-alpine as builder

WORKDIR /src

COPY package*.json ./

RUN npm install

COPY . .

RUN npm run build

FROM nginx:alpine

COPY --from=builder /src/build /usr/share/nginx/html

COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

COPY nginx/ssl /etc/nginx/ssl

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
