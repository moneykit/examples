# Usage: make <language>
# e.g. make python
#      make ruby


.PHONY: python
python:
	docker compose \
		-f docker-compose.yml \
		run -it --rm python

.PHONY: ruby
ruby:
	docker compose \
		-f docker-compose.yml \
		run -it --rm ruby

