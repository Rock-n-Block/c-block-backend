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
- ALLOWED_HOSTS -django allowed hosts list: list
- SECRET_KEY - django secret key: str
- DEBUG - django debug: bool
- TEST_ENDPOINT - celo web socket test RPC: str
- ENDPOINT - celo web socket RPC: str
- REDIS_EXPIRATION_TIME - redis expiration date: int
- REDIS_HOST - redis host: str
- REDIS_PORT - entry redis port: int
- EMAIL_HOST - login of the sender of the mail: str
- EMAIL_PASSWORD - password of the sender of the mail: str
### Тесты
```
docker-compose exec python manage.py test
```
