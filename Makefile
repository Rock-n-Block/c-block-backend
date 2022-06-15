include .env
compose_file := docker-compose.yaml
compose := docker-compose -f $(compose_file)
tail := 1000
service := web     # defaul service is web

build:
	$(compose) build --parallel

up_db:
	$(compose) up -d db

up:
	$(compose) up -d

up_service:
	$(compose) up -d $(service)

up_build: build
	$(compose) up -d

up_service_build: build
	$(compose) up -d $(service)

down:
	$(compose) down

# up_kibana:
# 	$(compose_kibana) up -d
#
# down_kibana:
# 	$(compose_kibana) down

make_all_migrations:
	$(compose) exec web python manage.py makemigrations contracts rates accounts

migrate_all:
	$(compose) exec web python manage.py migrate

createsuperuser:
	$(compose) exec web python manage.py createsuperuser

shell:
	$(compose) exec web python manage.py shell_plus

ps:
	$(compose) ps

logs:
	$(compose) logs --timestamps --tail $(tail) -f $(service)

pull_git:
	git pull origin ${git branch --show-current}

pull_docker:
	$(compose) pull

pull: pull_git pull_docker

update_migrate: down
	pull
	make_all_migrations
	migrate_all
	up

update: down
	pull
	up
