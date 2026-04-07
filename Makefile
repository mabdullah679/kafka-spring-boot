NETWORK_NAME := eclipse-net
PRODUCER_COMPOSE := producer-stack/docker-compose.yml
CONSUMER_COMPOSE := consumer-app/docker-compose.yml

.PHONY: help network-create network-remove build up down restart destroy ps logs logs-producer logs-consumer logs-data-sync logs-postgres

help:
	@echo "Targets:"
	@echo "  make up             Create network and start the full stack"
	@echo "  make build          Build all local images"
	@echo "  make down           Stop containers but keep the shared network"
	@echo "  make destroy        Stop containers and remove the shared network"
	@echo "  make restart        Recreate the full stack"
	@echo "  make ps             Show running project containers"
	@echo "  make logs           Tail logs for both compose projects"
	@echo "  make logs-producer  Tail kafka-producer logs"
	@echo "  make logs-consumer  Tail spring-consumer logs"
	@echo "  make logs-data-sync Tail data-sync logs"
	@echo "  make logs-postgres  Tail postgres logs"

network-create:
	@docker network inspect $(NETWORK_NAME) >/dev/null 2>&1 || docker network create $(NETWORK_NAME)

build:
	@docker compose -f $(PRODUCER_COMPOSE) build
	@docker compose -f $(CONSUMER_COMPOSE) build

up: network-create
	@docker compose -f $(PRODUCER_COMPOSE) up --build -d
	@docker compose -f $(CONSUMER_COMPOSE) up --build -d
	@$(MAKE) ps

down:
	@docker compose -f $(CONSUMER_COMPOSE) down --remove-orphans
	@docker compose -f $(PRODUCER_COMPOSE) down --remove-orphans

network-remove:
	@docker network rm $(NETWORK_NAME) >/dev/null 2>&1 || true

destroy: down network-remove

restart: destroy up

ps:
	@docker ps --filter "name=kafka" --filter "name=kafka-producer" --filter "name=spring-consumer" --filter "name=data-sync" --filter "name=eclipse-postgres"

logs:
	@docker compose -f $(PRODUCER_COMPOSE) logs -f &
	@docker compose -f $(CONSUMER_COMPOSE) logs -f

logs-producer:
	@docker logs -f kafka-producer

logs-consumer:
	@docker logs -f spring-consumer

logs-data-sync:
	@docker logs -f data-sync

logs-postgres:
	@docker logs -f eclipse-postgres
