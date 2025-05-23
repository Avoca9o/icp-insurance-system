---

# ICP Insurance System

ICP Insurance System — это децентрализованная страховая платформа, построенная на смарт-контрактах ICP. Проект предоставляет комплексное решение для страховых компаний и их клиентов, автоматизируя процессы страховых выплат, мониторинга и валидации страховых случаев с помощью различных сервисов.

## Сервисы репозитория

- **insurance_fund**  
  Смарт-контракты для управления активами страховых компаний и валидации страховых случаев.

- **insurer_backend**  
  Веб-сервер страховой компании для взаимодействия с фронтендом, смарт-контрактами и сторонними сервисами.

- **insurer_frontend**  
  Веб-приложение (админка) для сотрудников страховой компании для управления полисами, выплатами и пользователями.

- **open_banking_api_mock**  
  Мок-сервис для симуляции банковского API при валидации страховых случаев.

- **policy_holder_bot**  
  Telegram-бот [@PolicyHolder_bot](https://t.me/PolicyHolder_bot), через которого страхователь может запросить выплату.

---

## Быстрый старт

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/Avoca9o/icp-insurance-system.git
cd icp-insurance-system
```

### 2. Запустите все сервисы

Все сервисы, кроме смарт-контрактов (`insurance_fund`), поднимаются одной командой с помощью docker-compose:

```bash
docker compose up --build -d
```

> ⚠️ Убедитесь, что у вас установлен [Docker](https://www.docker.com/).

### 3. Разверните смарт-контракты локально

Для работы контрактов требуется Node.js v22. Установите его через nvm, а затем разверните смарт-контракты:

```bash
# Установите nvm (Node Version Manager)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash

# Перезапустите терминал или выполните команду ниже, чтобы nvm работал в текущей сессии
export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Установите Node.js v22
nvm install 22
nvm use 22

# Перейдите в папку со смарт-контрактами
cd insurance_fund

# Запустите локальный dfx и разверните контракты
dfx start --background
dfx deploy
```

---
### 4. Разверните frontend-админку

Для работы frontend необходима утилита npm, далее для развертывания необходимо выполнить следующие команды:

```bash
npm install
PORT=4000 npm start
```
По умолчанию npm разворачивает приложения на 3000 порту, но он занят другим контейнером в рамках нашей системы.

---

## Использование

- Страхователь обращается к телеграм-боту → создает страховой случай.
- Бэкенд получает запрос, проверяет условие (через open_banking_api_mock, смарт-контракт).
- При положительном результате страховой случай утверждается, выплата производится автоматически.

---

## Контакты

- Telegram для вопросов: [@Avoca9o](https://t.me/Avoca9o)
- Issues и Pull Requests приветствуются!

---

## Лицензия

MIT

---

**Будем рады вашим предложениям и участию в развитии проекта!**

---
