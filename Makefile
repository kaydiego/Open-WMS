.PHONY: up down logs shell restart install-module test

DB ?= fastlog
COMPOSE = docker compose -f docker/docker-compose.yml

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f odoo

shell:
	$(COMPOSE) exec odoo odoo shell -d $(DB)

restart:
	$(COMPOSE) restart odoo

install-module:
	$(COMPOSE) exec odoo odoo -d $(DB) -i fastlog_wms --stop-after-init

test:
	$(COMPOSE) exec odoo odoo -d $(DB) --test-enable --stop-after-init -i fastlog_wms
