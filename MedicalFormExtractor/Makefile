# grep the version from the mix file
VERSION=$(shell ./version.sh)
ACCOUNT=921386597848.dkr.ecr.us-east-1.amazonaws.com

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
	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $(ACCOUNT)

publish: build repo-login tag-latest publish-latest ## Publish the `{version}` ans `latest` tagged containers to ECR


tag-latest: ## Generate container `{version}` tag
	@echo 'create tag latest'
	docker tag form_extractor:latest ${ACCOUNT}/form_extractor:latest
publish-latest:
	docker push ${ACCOUNT}/form_extractor:latest

upload-config:
	aws s3 cp config.yml s3://data-store-igs/config/config.yml
	aws s3 cp icd10cm_tabular_2023.xml s3://data-store-igs/config/icd10cm_tabular_2023.xml
	aws s3 cp icd10_desc.json s3://data-store-igs/config/icd10_desc.json
	aws s3 cp icd_dump.json s3://data-store-igs/config/icd_dump.json

update-lambda:
	SHA=$(docker images --no-trunc --quiet "${ACCOUNT}"/form_extractor:latest)
	aws lambda update-function-code --function-name  process_pdf --image-uri $(SHA)
