#!/bin/bash

ARGS=$@

read -p "Введите путь до входного файла: " input
read -p "Введите путь куда сохранить результат: " output

python -m \
	pip install \
	--user dist/compliance_atom-1.0.0-py3-none-any.whl

python -m compliance.main \
	-i $input \
	-o $output
