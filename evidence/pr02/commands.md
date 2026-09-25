# ПР02: команды и наблюдения

Опыт проведён 25 сентября 2026 года на Ubuntu с ROS 2 Lyrical. Во всех
терминалах использован `ROS_DOMAIN_ID=87`. Настоящий `turtlesim_node` запущен
с `QT_QPA_PLATFORM=offscreen`, поэтому окно не выводилось. Движение проверено
по `Pose` и состоянию графа ROS 2. Нода teleop в этом опыте не запускалась.

## Терминал и пакет

Рабочий каталог — корень этого репозитория. `pwd` показывает текущий каталог;
`cd` его меняет, `ls -a` показывает в том числе скрытые файлы, а `printenv`
читает переменные среды. `source /opt/ros/lyrical/setup.bash` настраивает ROS
в текущей оболочке; после сборки `source install/setup.bash` добавляет пакет.
`export ROS_DOMAIN_ID=87` задаёт домен дочерним процессам. Во всех терминалах
нужен одинаковый домен.

Команда `ros2 pkg create --build-type ament_python --license Apache-2.0
turtle_bringup --dependencies launch launch_ros turtlesim` создала пакет в
`src/` с именем и адресом автора из настроек этого репозитория. До добавления
launch выполнена первая сборка:

```bash
colcon build --symlink-install --packages-select turtle_bringup \
  > evidence/pr02/build-empty.txt 2>&1
```

В [build-empty.txt](build-empty.txt) пакет собран успешно. Затем добавлен
`launch/sim.launch.py`, а `setup.py` дополнен установкой launch через
`data_files`. После повторной сборки в [build.txt](build.txt) пакет снова
успешен. `ros2 pkg prefix turtle_bringup` вернул
`/home/ubuntu/robotics/install/turtle_bringup`
([package-prefix.txt](package-prefix.txt)); установленный launch-файл найден.
Оператор `>` записывает stdout в файл, `2>&1` присоединяет stderr, а `|`
передаёт вывод следующей команде. `mkdir -p` создаёт каталог, если его ещё нет.
Сборка сама по себе ноду не запускает.

`python3 -m py_compile src/turtle_bringup/launch/sim.launch.py` и проверка
установленного файла завершились с кодом 0. Тесты каркаса выполнены из каталога
пакета: `python3 -m pytest test -q` — 4 passed, 1 skipped
([package-tests.txt](package-tests.txt)). Пропущен сгенерированный тест
copyright.

## Запуск и остановка

В терминале A после подключения ROS и сборки:

```bash
export ROS_DOMAIN_ID=87
export QT_QPA_PLATFORM=offscreen
ros2 launch turtle_bringup sim.launch.py
```

В B команда `ros2 node list --no-daemon --spin-time 2` показала `/turtlesim`
([nodes-running.txt](nodes-running.txt)). После Ctrl+C нода исчезла
([nodes-stopped.txt](nodes-stopped.txt)), а процесс завершился штатно
([launch-first.txt](launch-first.txt)). Для опыта launch запущен повторно;
это подтверждают [nodes-restarted.txt](nodes-restarted.txt) и
[launch-experiment.txt](launch-experiment.txt).

## Правильная команда и диагностика сбоя

Начальная поза получена через `ros2 topic echo /turtle1/pose --once`. В B
отправлена одна команда:

```bash
ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```

После остановки черепахи запущен издатель с **ошибочным** именем:

```bash
ros2 topic pub --rate 1 --wait-matching-subscriptions 0 \
  /cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```

В C проверены `ros2 topic info /cmd_vel --verbose`,
`ros2 topic info /turtle1/cmd_vel --verbose` и новая поза. У `/cmd_vel` был
1 издатель и 0 подписчиков ([topic-broken.txt](topic-broken.txt)); у
`/turtle1/cmd_vel` — 0 издателей и 1 подписчик
([topic-target-before-fix.txt](topic-target-before-fix.txt)). Поза не изменилась.

После Ctrl+C ошибочному издателю изменено **только имя** топика:

```bash
ros2 topic pub --rate 1 --wait-matching-subscriptions 0 \
  /turtle1/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```

При первой быстрой проверке после старта ROS CLI ответил `Unknown topic`:
обнаружение издателя ещё не завершилось. Повтор показал 1 издателя и
1 подписчика ([topic-fixed.txt](topic-fixed.txt)). Команда поменяла позу.
После Ctrl+C скорости стали нулевыми. Это фиксирует фактические значения
одного прогона; долгая непрерывная публикация успела повернуть черепаху
дальше точки после первой команды.

| Состояние | x | y | theta, рад | linear_velocity | angular_velocity |
| --- | ---: | ---: | ---: | ---: | ---: |
| До команды | 5.544445 | 5.544445 | 0.000000 | 0.0 | 0.0 |
| После одной правильной команды | 6.509309 | 5.796991 | 0.504000 | 0.0 | 0.0 |
| Во время ошибочной публикации | 6.509309 | 5.796991 | 0.504000 | 0.0 | 0.0 |
| Во время исправленной публикации | 3.563402 | 7.871734 | -1.739185 | 1.0 | 0.5 |
| После остановки издателя | 5.933712 | 9.504587 | 2.937629 | 0.0 | 0.0 |

Исходные сообщения: [pose-before.txt](pose-before.txt),
[pose-working.txt](pose-working.txt), [pose-broken.txt](pose-broken.txt),
[pose-fixed.txt](pose-fixed.txt), [pose-resting.txt](pose-resting.txt).
Тип сообщения позы приведён в [types.md](types.md). После остановки launch
[nodes-final.txt](nodes-final.txt) пуст.
Дополнительная сверка сохранённых значений, числа endpoint и остановки ноды
завершилась успешно ([observations-check.txt](observations-check.txt)).

Причина сбоя — полное имя `/cmd_vel` не совпадает с именем подписки turtlesim
`/turtle1/cmd_vel`. Одинаковый тип `Twist` сам по себе не связывает эти топики.
