# C-Block
## Description
- [x] Contract history for:
  - [x] Tokens
  - [x] Crowdsales
  - [x] Wedding contracts
  - [x] LastWill/LostKey contract 
- [x] Scanner for events on factories
- [x] API for retrieving user history
- [x] API for creating of new contracts
## Components
- Web (Django)
- Event scanner (websockets)
- Database (PostgreSQK)
- Periodic tasks (celery + redis + scheduler) 
## Services
- Django
- Celery
- Postgresql
- Scheduler
- Redis
### Build
```
make up
```
```
make make_all_migrations
```
```
make migrate_all
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
  - token_factories:
    - token address
    - token address
    - token address
    - token address
  - crowdsale_factories:
    - crowdsale address
    - crowdsale address
  - lastwill_factories:
    - lastwill address
  - lostkey_factories:
    - lostkey address
  - wedding_factories:
    - wedding address
    - wedding address
  - test: test network or not
  - day_seconds: 60
  - confirmation_checkpoints: [ 5, 10, 15 ]
- network:
  - ws_endpoint: 'wss://forno.celo.org/ws'
  - rpc_endpoint: 'https://forno.celo.org'
  - token_factories:
    - token address
    - token address
    - token address
    - token address
  - crowdsale_factories:
    - crowdsale address
    - crowdsale address
  - lastwill_factories:
    - lastwill address
  - lostkey_factories:
    - lostkey address
  - wedding_factories:
    - wedding address
    - wedding address
  - test: test network or not
  - day_seconds: 86400
  - confirmation_checkpoints: [ 1, 3, 7 ]
### Tests
```
docker-compose exec web python manage.py test
```
