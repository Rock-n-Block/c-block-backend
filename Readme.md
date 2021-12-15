# C-Block
## Описание
- [x] Сохранение истории контрактов токенов
- [x] Сохранение истории контрактов краудсейлов
- [x] Сохранение истории контрактов завещания
- [x] Сохранение истории контрактов свадебных
- [x] Сканер евентов фабрик
- [x] Ручки для отдачи истории пользователей
- [x] Ручка для сохранения новых контрактов
## Компоненты
- Веб на django
- Сканнер евентов web sockets
- База данных postgresql
- Периодические задачи celery + redis + scheduler
## Сервисы
- Django
- Celery
- Postgresql
- Scheduler
- Redis
### Сборка
```
docker-compose up -d --build
```
```
docker-compose exec web python manage.py makemigrations
```
```
docker-compose exec web python manage.py migrate
```
### .env file
- DJANGO_PORT - entry port
- DOCKER_EXPOSE_PORT - expose port
- FLOWER_PROT - flower entry and expose port
- POSTGRES_DB - database name
- POSTGRES_USER- database user
- POSTGRES_PASSWORD - database password
- POSTGRES_HOST - database host
- POSTGRES_PORT - entry port
- REDIS_HOST - broker host
- REDIS_PORT - entry port

### config.py
- allowed_hosts: list allowed hosts
- secret_key: some django secret key
- debug: on or off debug
- static_url: urlpath to statis
- static_root: path to static files
- redis_expiration_time: expiration time
- redis_host: redis host
- redis_port: port
- email_host: smtp server
- email_host_user: admin mail for sending mails
- email_password: admin mail password
- email_port: smtp server port
- test_network:
  - ws_endpoint: 'wss://alfajores-forno.celo-testnet.org/ws'
  - rpc_endpoint: 'https://alfajores-forno.celo-testnet.org'
  - token_address:
    - token address
    - token address
    - token address
    - token address
  - crowdsale_address:
    - crowdsale address
    - crowdsale address
  - probate_address:
    - probate address
    - probate address
  - wedding_address:
    - wedding address
    - wedding address
  - test: test network or not
- network:
  - ws_endpoint: 'wss://forno.celo.org/ws'
  - rpc_endpoint: 'https://forno.celo.org'
  - token_address:
    - token address
    - token address
    - token address
    - token address
  - crowdsale_address:
    - crowdsale address
    - crowdsale address
  - probate_address:
    - probate address
    - probate address
  - wedding_address:
    - wedding address
    - wedding address
  - test: test network or not
### Тесты
```
docker-compose exec web python manage.py test
```
