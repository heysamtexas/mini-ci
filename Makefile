TAG = runner

.PHONY: run
run:
	docker run -it --rm -e $(TAG) python /runner.py

.PHONY: stop
stop:
	docker-compose down

.PHONY: build
build:
	docker build -t $(TAG) .

.PHONY: start
start:
	docker-compose up -d

.PHONY: logs
logs:
	docker-compose logs -f

.PHONY: clean
clean:
	rm -rf workspace/*
