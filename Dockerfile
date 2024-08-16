FROM node:latest
COPY package.json ./package.json
RUN npm install
COPY . .
RUN chmod +x ./start.sh
