# grep the version from the mix file
VERSION=$(shell ./version.sh)


# HELP
# This will output the help for each task
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help

help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help


build:
	docker build -t form_extractor .

repo-login:
	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 921386597848.dkr.ecr.us-east-1.amazonaws.com

publish: build repo-login tag-latest publish-latest ## Publish the `{version}` ans `latest` tagged containers to ECR


tag-latest: ## Generate container `{version}` tag
	@echo 'create tag latest'
	docker tag form_extractor:latest 921386597848.dkr.ecr.us-east-1.amazonaws.com/form_extractor:latest
publish-latest:
	docker push 921386597848.dkr.ecr.us-east-1.amazonaws.com/form_extractor:latest

