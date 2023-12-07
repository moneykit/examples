# Usage: make run backend=<lang> frontend=<platform>
# e.g. make run frontend=ios
# e.g. make run backend=ruby frontend=android
# e.g. make run backend=go

# python  | ruby
backend := python


.PHONY: run
run:
	BACKEND=$(backend) ./run.sh

.PHONY: stop
stop:
	docker compose \
		-f docker-compose.yml \
		down
