FROM node:9-slim

WORKDIR /app
COPY . /app
RUN npm install
EXPOSE 80
CMD ["node", "./bin/www"]