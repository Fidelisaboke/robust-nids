# Makefile for Docker / Docker Compose workflows

# The compose file to use
COMPOSE = docker compose
COMPOSE_FILE = docker-compose.yml

# Allow passing “c=service_name” to limit commands to a specific service
SERVICE ?=

# Phony targets (not files)
.PHONY: help build up start down destroy logs ps clean-maybe

help:
	@echo "Make commands for Docker Compose:"
	@echo "  make build [c=service]       Build (or rebuild) images"
	@echo "  make up [c=service]          Start containers (in background)"
	@echo "  make start [c=service]       Start stopped containers"
	@echo "  make down [c=service]        Stop & remove containers, networks"
	@echo "  make destroy [c=service]     Down + remove volumes"
	@echo "  make logs [c=service]        Tail logs"
	@echo "  make ps                      List running containers"
	@echo "  make clean-maybe             Clean up unused (prune) images/volumes"

build:
	$(COMPOSE) -f $(COMPOSE_FILE) build $(SERVICE)

up:
	$(COMPOSE) -f $(COMPOSE_FILE) up -d $(SERVICE)

start:
	$(COMPOSE) -f $(COMPOSE_FILE) start $(SERVICE)

down:
	$(COMPOSE) -f $(COMPOSE_FILE) down $(SERVICE)

destroy:
	$(COMPOSE) -f $(COMPOSE_FILE) down -v $(SERVICE)

logs:
	$(COMPOSE) -f $(COMPOSE_FILE) logs --tail=100 -f $(SERVICE)

ps:
	$(COMPOSE) -f $(COMPOSE_FILE) ps

clean-maybe:
	@echo "Pruning unused Docker objects..."
	docker system prune -af
