FROM node:13

RUN mkdir /alephui
WORKDIR /alephui

COPY .npmrc /alephui/.npmrc
COPY scripts /alephui/scripts
COPY config /alephui/config
COPY package.json /alephui

RUN npm install --verbose

COPY i18n /alephui/i18n
COPY public /alephui/public
COPY src /alephui/src

ENV REACT_APP_API_ENDPOINT /api/2/
# RUN npm run build
