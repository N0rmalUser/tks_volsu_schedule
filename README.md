# Администрирование бота для самых маленьких

[![license](https://img.shields.io/badge/🖥️-Ссылка_на_бота-77dd77)](https://t.me/tks_schedule_bot)  

## Предупреждение
___Ребята не стоит вскрывать эту тему. Вы молодые, шутливые, вам всё легко. Это не то. Это не Чикатило и даже не архивы спецслужб. Сюда лучше не лезть. Серьёзно, любой из вас будет жалеть. Лучше закройте тему и забудьте что тут писалось. Я вполне понимаю что данным сообщением вызову дополнительный интерес, но хочу сразу предостеречь пытливых - стоп. Остальных просто не найдут.___

## Как быстро развернуть бота на сервере в 2-13
1. Установить токен бота и id чата в `config.toml`
2. Собрать контейнер
3. Прийти в 2-13
4. Подключиться к сети
5. Запустить `deploy.ps1`, указав пароль админа

## Где находятся настройки бота
Все настройки находятся в файле `config.toml`
Там же списки всех преподавателей, увс, колледжских, групп и кабинетов

## Как получить базу данных с расписаниями
* Расписания колледжа (`xlsx`) и университета (`docs` НЕ `PDF`!) засунуть в `/preparation/schedules/`
* Расписание университетских групп должно быть разделено на фалы по подгруппам (РСК-211 - первая подгруппа, РСК-211_2 - вторая)
* Затем запустить файл `university_converter.py` и `college_converter.py`
* Переместить полученный файл в `data/` (если в `config.py` не указан другой путь)

## Как заменить бд в боте
Через `#General` закинуть файлы баз данных с названием:
   * `activities.db` - активность пользователей  
   * `schedule.db` - расписание
   * `users.db` - данные пользователей
   __Если название будет другим, ничего не поменяется!__

## Как отправлять сообщения пользователям бота
В `config.toml` есть переменная `admin_chat_id`, указывающая id чата,
в котором создаются топики пользователей, нажавших на кнопку "Начать" в боте.  
Написав сообщение в этот чат, оно будет отправлено этому пользователю.  
Если отправить сообщение в "General", сообщение получат все пользователи бота.
Команды пользователям не отправляются.

## Какие команды поддерживает бот
### Обычные юзвери могут использовать только:
| Команда   | Пояснение                                                                                                                          |
|-----------|:-----------------------------------------------------------------------------------------------------------------------------------|
| `/start`  | Начать работу с ботом                                                                                                              |
| `/help`   | Выводит текст, объясняющий, что да как в боте                                                                                      |
| `/admin`  | Написать админу (в админском чате появится сообщение с просьбой о помощи и автоматом врубится слежение за действиями пользователя) |


### Админы могут использовать те же команды, что и юзвери, а также:
| Команда         | Пояснение                                                                                                                                           |
|-----------------|:----------------------------------------------------------------------------------------------------------------------------------------------------|
| `/dump`         | Последовательная отправка файла логов, его отчистка, отправка базы данных                                                                           |
| `/info`         | Присылает всю ключевую инфу пользователя из бд (не работает в "General")                                                                            |
| `/hours_stat`   | Статистика пользователей по часам за определённый день в формате DD.MM.YY. Если ничего не присылать, показывает статистику за сегодня.              |
| `/days_stat`    | Статистика пользователей по дням за последние 30 дней.                                                                                              |
| `/track start`  | Включить слежение за действиями пользователя (если написан в топике, то только за этим юзером, если в "General", то за всеми)                       |
| `/track stop`   | Выключить слежение за действиями пользователя. Те же правила, что и при start                                                                       |
| `/track status` | Проверить, включено ли слежение за действиями пользователя. Если написать в General, показывает список пользователей, за которыми включено слежение |
| `/teacher`      | Меняет тип пользователя на преподавателя                                                                                                            |
| `/student`      | Меняет тип пользователя на студента                                                                                                                 |
| `/bun`          | Банит пользователя, не обрабатывая его сообщения и нажатия на кнопки                                                                                |
| `/unbun`        | Отмена бана                                                                                                                                         |
| `/log`          | Отправляет только файл логов и очищает его на сервере.                                                                                                                             |
| `/day`          | Статистика пользователей по часам за определённый день в формате DD.MM.YY. Если ничего не присылать, показывает статистику за сегодня.                                             |
| `/month`        | Статистика пользователей по дням за последние 30 дней с указанной даты в формате DD.MM.YY. Если ничего не присылать, показывает статистику за сегодня.                             |
  
__Админские команды работают только в группе и не пересылаются пользователям__

Можно переименовывать топики и изменять их иконки. Всё завязано на id топика и группы, так что это ни как не повлияет на работу бота.
