#!/bin/bash

ARGS=$@

read -p "Введите путь до входного файла: " input
read -p "Введите путь куда сохранить результат: " output

python -m \
	pip install \
	--user dist/compliance_atom-1.0.0-py3-none-any.whl

mkdir -p "$(pwd)/.logs/"

python -m compliance.main \
	-i $input \
	-o $output \
	> "$(pwd)/.logs/app_stdout_$(date --utc +%Y_%m_%dT%H_%M_%S).log"
