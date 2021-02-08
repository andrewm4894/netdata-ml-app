ENV=local
APP=netdata-ml-app

.PHONY: build
build:
	docker build -t $(APP) . --build-arg ENV=$(ENV)

.PHONY: stop
stop:
	@echo "Stopping existing containers..."
	@eval $$(docker ps -a | grep $(APP) | awk '{print $$1}' | xargs docker stop > /dev/null 2>&1)

.PHONY: start
start: stop
	docker run --rm -d -p 29999:29999 -e LOG_LEVEL=DEBUG $(APP)

.PHONY: logs
logs:
	@docker ps -a | grep $(APP) | awk '{print $$1}' | xargs docker logs -f

.PHONY: test
test:
	cd app; pytest