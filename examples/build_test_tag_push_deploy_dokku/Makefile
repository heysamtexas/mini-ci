SITE_VERSION := $(shell semver.sh bump patch)

DOCKER_RUN := docker run -it --rm -p 5000:5000 -v $$PWD:/usr/src/app --env-file=env $(IMAGE_NAME)

DOCKER_TAG := $(IMAGE_NAME):$(SITE_VERSION)

.PHONY: build
build:
	docker build --build-arg SITE_VERSION=$(SITE_VERSION) -t $(DOCKER_TAG) .


.PHONY: run
run:
	$(DOCKER_RUN) $(CMD)

.PHONY: test
test:
	$(DOCKER_RUN) /app/manage.py test


.PHONY: migrate
migrate:
	$(DOCKER_RUN) ./manage.py makemigrations
	$(DOCKER_RUN) ./manage.py migrate


.PHONY: cachetable
cachetable:
	$(DOCKER_RUN) ./manage.py createcachetable


.PHONY: clean
clean:
	find src/ -type f -name *.pyc -delete
	find src/ -type d -name __pycache__ -delete


##### CI/CD Server commands

.PHONY: ci-deploy
ci-deploy: build

	@echo "****************"
	@echo "Running tests..."
	@echo "****************"
	docker-compose -p $(DOKKU_APP_NAME)_test -f docker-compose-test.yml run --rm website /app/manage.py test
	docker-compose -p $(DOKKU_APP_NAME)_test -f docker-compose-test.yml down

	@echo "***************************"
	@echo "Tagging and pushing repo..."
	@echo "***************************"
	git tag $(SITE_VERSION)
	git push origin $(SITE_VERSION)

	@echo "***********************"
	@echo "Pushing docker image..."
	@echo "***********************"
	docker login -u $(DOCKER_USER) -p $(DOCKER_PASS)
	docker push $(DOCKER_TAG)

	@echo "************"
	@echo "Deploying..."
	@echo "************"
	ssh-keyscan $(DOKKU_HOST) >> /$(HOME)/.ssh/known_hosts
	ssh $(DOKKU_DEPLOY_USER)@$(DOKKU_HOST) pull $(IMAGE_NAME):$(SITE_VERSION)
	ssh $(DOKKU_DEPLOY_USER)@$(DOKKU_HOST) tag $(IMAGE_NAME):$(SITE_VERSION) dokku/$(DOKKU_APP_NAME):$(SITE_VERSION)
	ssh dokku@$(DOKKU_HOST) tags:deploy $(DOKKU_APP_NAME) $(SITE_VERSION)

.PHONY: bump
bump:
	git commit -m 'dummy bump' bumpfile
	git push github master
