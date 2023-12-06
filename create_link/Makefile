# Usage: make run backend=<lang> frontend=<platform>
# e.g. make run frontend=ios
# e.g. make run backend=ruby frontend=android
# e.g. make run backend=go

# web | ios | android | react_native
frontend := web
# python | python_without_sdk | ruby
backend := python


.PHONY: run
run:
	BACKEND=$(backend) FRONTEND=$(frontend) ./run.sh

.PHONY: stop
stop:
	docker compose \
		-f docker-compose.yml \
		down
