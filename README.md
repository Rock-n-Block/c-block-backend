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

See `config.example.yaml` for all info


### Setup site name

```bash
docker compose exec web python manage.py setup_site app.cblock.io 'C-Block Platform'
```

### Create super user

```bash
make createsuperuser
```

### Tests
```
docker-compose exec web python manage.py test
```