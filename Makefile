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
	@cd compliance; \
	nohup uvicorn qwen_main:app --reload --host 0.0.0.0 --port 8000 2>&1 &
	# port forward
	# netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=8000 connectaddress=<WSL_IP> connectport=8000
	# port proxy list
	# netsh interface portproxy show all
	# port proxy delete
	# netsh interface portproxy delete v4tov4 listenaddress=<WSL_IP> listenport=8000

stop-llm:
	@pkill -9 -f uvicorn

run-app:
	@poetry run compliance -i data/test.zip -o data/test_output.xlsx > ".logs/app_stdout_$(shell date --utc +%Y_%m_%dT%H_%M_%S).log"
