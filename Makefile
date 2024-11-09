.EXPORT_ALL_VARIABLES:
SHELL=/bin/bash
PROJECT_DIR=/app
PYTHONPATH=$(shell pwd)
ENV_FILE = .env

ifneq (,$(wildcard $(ENV_FILE)))
	include $(ENV_FILE)
	export
endif

test-env:
	@echo "API_TOKEN is $(LLM_API_TOKEN)"

run-llm:
	@cd src; \
	uvicorn qwen_main:app --reload --host 0.0.0.0 --port 8000
	# port forward 
	# netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=8000 connectaddress=<WSL_IP> connectport=8000
	# port proxy list
	# netsh interface portproxy show all
	# port proxy delete
	# netsh interface portproxy delete v4tov4 listenaddress=<WSL_IP> listenport=8000
