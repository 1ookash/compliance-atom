# Проект команды SD Eagles

## Минимальные необходимые зависимости

* python 3.11 или версией выше
* Linux

## Необходимые зависимости

* poetry
* make

## Описание репозитория

В данном репозитории объеденнены несколько сервисов конечного продука:

1. qwen app - приложение для доступа к LLM по АПИ. В данный момент развернуто на выделенной машине хакатона
2. compliance app - приложение для обработки документации и выдачи конечного результата в формате таблицы

## Запуск алгоритма

Для локального запуска алгоритма необходимо иметь только системный python версии 3.11 или выше. Перед запуском необходимо создать файл .env:

```bash
cp .env_example .env
```

В полученном .env файле необходимо указать путь до роута к REST API и путь до файла с БД SQLite.

Запуск осуществляется через вызов из под системы UNIX файла FULL_LAUNCH.sh.

```bash
./FULL_LAUNCH.sh
```

После запуска файла в консоли необходимо ввести путь до zip архива с данными и путь, по которому будет сохранен результат.

Во время исполнения можно наблюдать логи, они будут писаться в .logs/app_stdout_timestamp.log, и ответы LLM, они будут в data/app_run_timestamp/.

## Сборка среды

Для дальнейшей разработки или запуска сервиса с REST API необходимо собрать среду python. Среда описана в pyproject.toml и устанавливается вызовом команды:

```bash
poetry install --with qwen
```

## Деплой REST API

Для деплоя необходима утилита make. Перед деплоем в .env необходимо указать абсолютный путь до модели. Деплой описан в Makefile и вызывается командой:

```bash
make run-llm
```
