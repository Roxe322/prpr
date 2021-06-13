# prpr

![example workflow](https://github.com/salmiakki/prpr/actions/workflows/actions.yaml/badge.svg)

Вряд ли вы здесь случайно.

## Как воспользоваться

Нужен Python 3.9+.

### Dotfile

В `~/.prpr.yaml` нужно положить токен доступа к Стартреку,
определить первое число для начала месяца расчёта зарплаты,
определить суффиксы для уточнения когорт (в зависимости от курса):

```yaml
startrek_token: your_token_here
# Optional:
month_start: 16  # Meaning closed tickets are grouped by May 16-June 15, June 16-July 16 and so on.
component_suffixes:  # suffixes for cohort definition according to course
  backend-developer: ''
  python-developer-plus: '+'
```

### Запуск

Клонируем, (по желанию) создаем окружение, ставим зависимости.

```bash
python3 -m prpr.main
```

Также удобно создать bash alias,
чтобы можно было запускать из любого местоположения, например, так:

```
alias prpr='cd /path/to/dir/prpr/ && source venv/bin/activate && python -m prpr.main'
```

### Опции запуска

Доступна встроенная справка:

```bash
python3 -m prpr.main --help
```

```
usage: main.py [-h] [-m {standard,all,open,closed,closed-this-month,closed-previous-month}] [-p PROBLEMS [PROBLEMS ...]] [-n NO] [-s STUDENT] [-c COHORTS [COHORTS ...]] [-f FROM_DATE] [-t TO_DATE] [-o] [-d] [--head] [-i] [-v] [--post-process]

optional arguments:
  -h, --help            show this help message and exit
  -o, --open            open homework pages in browser
  -v, --verbose

filters:
  these allow to specify the subset of homeworks to be displayed, can be composed

  -m {standard,all,open,closed,closed-this-month,closed-previous-month}, --mode {standard,all,open,closed,closed-this-month,closed-previous-month}
                        filter mode
                                    standard: in review, open or on the side of user
                                    open: in review or open
                                    closed: resolved or closed
                                    closed-this-month: resolved or closed this "month" aka 💰.
                                    closed-previous-month: resolved or closed previous "month" aka 💰.
                                    all: all, duh
  -p PROBLEMS [PROBLEMS ...], --problems PROBLEMS [PROBLEMS ...]
                        the numbers of problems to be shown; multiple space-separated values are accepted
  -n NO, --no NO        the no of the homework to be shown, all other filters are ignored
  -s STUDENT, --student STUDENT
                        the substring to be found in the student column, mail works best
  -c COHORTS [COHORTS ...], --cohorts COHORTS [COHORTS ...]
                        cohorts to be shown; multiple space-separated values are accepted
  -f FROM_DATE, --from-date FROM_DATE
                        the start date (YYYY-MM-DD)
  -t TO_DATE, --to-date TO_DATE
                        the end date (YYYY-MM-DD)

download:
  -d, --download
  --head                download with visible browser window (default is headless, i.e. the window is hidden)
  -i, --interactive     choose which homework to download interactively

process:
  --post-process
```

### Примеры использования опций запуска

Вывести только 1 и 2 проекты для студентов 16 когорты и 1 когорты "Питон+":

```bash
python -m prpr.main --problems 1 2 --cohorts 16 1+
```

Открыть в браузере работу № 100:

```bash
python -m prpr.main --no 100 --open
```

Скачать архив с работой:

```bash
python -m prpr.main --down
```

Вывести все работы по конкретному студенту (емейл, имя, фамилия):
```bash
python -m prpr.main --mode all --student ivanov@yatube.ru
python -m prpr.main --mode all --student "Василиса Пупкина"
```

Вывести все закрытые работы в определенный период времени.
Даты указываются в формате YYYY-MM-DD:
```bash
python -m prpr.main --mode closed --from-date 2021-04-16 --to-date 2021-05-15
```

Вывести закрытые в текущем/предыдущем учетном месяце работы:

```bash
python -m prpr.main --mode closed-this-month
python -m prpr.main --mode closed-previous-month
```

## Как работают итерации

Номер итерации равен количеству переходов в статус `Открыт`.

Получение истории статусов требует отдельного запроса на каждый тикет,
так что (пока?) для экономии номер итерации отображается только для заданий
со статусом `Открыт` или `Ревью`.

## Как настроить скачку

1. [Установить драйвер Selenium](https://selenium-python.readthedocs.io/installation.html#drivers) для Firefox.
1. До Ревизора должен быть доступ (VPN, 2FA etc).
1. Нужно указать в `.prpr` [профиль Firefox](https://support.mozilla.org/en-US/kb/profiles-where-firefox-stores-user-data) с залогином в Ревизоре.

```yaml
# .prpr fragment
download:
    directory: path/to/downloaded/homeworks
    browser:
        type: firefox
        profile_path: path/to/firefox/profile
```

## Как работает скачка

В тикете есть ссылка на Ревизор. Она открывается в Firefox с помощью Selenium 🤦🏻‍♀️,
там кликается нужная вкладка. Из страницы вынимаются ссылки на zip-файлы. Недостающие
архивы скачиваются в директорию, указанную в дотфайле. Нужная структура поддиректорий
будет создана автоматически.

## История изменений

### 2021-06-13

* Домашнюю работу для скачивания можно выбрать интерактивно: `-i/--interactive`.

### 2021-06-09

* Добавлен пост-процессинг aka «диффы» 🥳

### 2021-06-04

* Архивы распакуются при скачке.

### 2021-05-31

* Теперь можно скачать архивы с домашними заданиями, пока только через Firefox.
* Теперь `-v` включает логи со статусом INFO и выше, `-vv` -- со статусом `DEBUG` и выше.
* Ссылка на Стартрек не обрезается на узких терминалах.

### 2021-05-30

* Добавлен режим `closed-previous-month`.

### 2021-05-29

* Добавлен вывод когорт в таблицу.
* Добавлен фильтр по когортам.

### 2021-05-27

* Добавлен режим `closed-this-month`.
* Ключи фильтров по датам переименованы в `--date-from` и `--date-to`.
* Режим `default` переименован в `standard`.

### 2021-05-26

* Добавлена поддержка фильтров по дате.

### 2021-05-24

* Добавлена поддержка номеров итераций и отображение дедлайнов для тикетов в статусе `Ревью`.

### 2021-05-20

* Добавлены примеры запусков.

## Тубидубидутуду

1. Настройки и украшения
1. Создать пакет cо скриптом запуска
1. Уведомления
1. Статистика
1. Тесты 😹
1. Кэширование
1. Демонстрационный запуск
