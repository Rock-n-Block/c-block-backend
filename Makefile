include .env
compose_file := docker-compose.yaml
compose := docker-compose -f $(compose_file)

build:
	$(compose) build --parallel

up_db:
	$(compose) up -d db

up: build
	$(compose) up -d

down:
	$(compose) down

up_kibana:
	$(compose_kibana) up -d

down_kibana:
	$(compose_kibana) down

make_all_migrations:
	$(compose) exec web python manage.py makemigrations scanner

migrate_all:
	$(compose) exec web python manage.py migrate

shell:
	$(compose) exec web python manage.py shell_plus

ps:
	$(compose) ps -a $(service)

logs:
	$(compose) logs -f $(service)
