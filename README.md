# ПР05. Launch, QoS и повтор записи

Ветка `pr05` продолжает ПР04. Пакет `course_bringup` одной командой запускает
глобальный `turtlesim`, `patrol` и две ноды в пространстве имён `/robot_a`:
`pose_relay` пересылает позу в `/robot_a/sensor_pose` с QoS `best_effort`,
`pose_monitor` подписывается с выбранной надёжностью. Выход `patrol` через
remap подключён к `/turtle1/cmd_vel`. Все имена топиков в собственных нодах
относительные; входные и выходные связи задаёт launch-файл.

Из корня репозитория:

```bash
source /opt/ros/lyrical/setup.bash
export ROS_DOMAIN_ID=105 QT_QPA_PLATFORM=offscreen
colcon build --symlink-install --packages-select turtle_bringup patrol course_bringup
source install/setup.bash
ros2 launch course_bringup patrol.launch.py \
  namespace:=robot_a subscriber_reliability:=reliable record:=false
```

В другом терминале с тем же `source` и `ROS_DOMAIN_ID` видно, что
`/robot_a/sensor_pose` существует, но `reliable`-подписчик не получает
сообщения от `best_effort`-издателя:

```bash
ros2 topic info /robot_a/sensor_pose --verbose
timeout -k 2s 3s ros2 topic echo /robot_a/sensor_pose \
  --qos-reliability reliable --once
```

Остановите launch и запустите исправленный профиль вместе с записью MCAP:

```bash
ros2 launch course_bringup patrol.launch.py \
  namespace:=robot_a subscriber_reliability:=best_effort \
  record:=true bag_dir:=evidence/pr05/bag
```

После нескольких секунд остановите launch, затем воспроизведите запись с
`config/qos-overrides.yaml` и проверьте оба профиля подписчика:

```bash
ros2 bag play evidence/pr05/bag --loop \
  --qos-profile-overrides-path config/qos-overrides.yaml
ros2 bag info evidence/pr05/bag
```

Фактические команды и ответы сохранены в
[qos-before.txt](evidence/pr05/qos-before.txt) и
[qos-after.txt](evidence/pr05/qos-after.txt); файл
[bag-metadata.yaml](evidence/pr05/bag-metadata.yaml) скопирован из записи.
Проверка проекта:

```bash
python3 -m pytest src/course_bringup/test src/patrol/test -q
colcon test --packages-select turtle_bringup patrol course_bringup
colcon test-result --verbose
python3 .course-kit/v1/tools/check_practice.py PR05 --submission .
```

Для checker нужен комплект курса `v1-w05`, SHA-256 архива
`bca214e3de6f90f9513049dfa0f36fee65ad834da502dc3f3f8fb443517b5197`.

# ПР04. Параметризуем движение

Ветка `pr04` продолжает ПР03. Нода `patrol` использует параметры
`linear_speed` (0–1 м/с, по умолчанию 0.5), `turn_rate` (−1–1 рад/с,
по умолчанию 0.3) и `publish_hz` (1–30 Гц, по умолчанию 10.0).
Все значения должны быть конечными. Недопустимое обновление отклоняется до
изменения команды или таймера. При смене частоты старый таймер удаляется.

Из корня репозитория:

```bash
source /opt/ros/lyrical/setup.bash
export ROS_DOMAIN_ID=87
colcon build --symlink-install --packages-select turtle_bringup patrol
source install/setup.bash
ros2 launch turtle_bringup sim.launch.py
```

В другом терминале с теми же `source` и `ROS_DOMAIN_ID`:

```bash
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

В третьем терминале меняйте параметры и измеряйте поток команд:

```bash
ros2 param set /patrol publish_hz 5.0
ros2 param set /patrol publish_hz 0.0
ros2 param get /patrol publish_hz
ros2 topic hz /turtle1/cmd_vel
```

Ноль отклоняется, частота остаётся 5 Гц. Команды и фактические результаты
записаны в [evidence/pr04/parameters.md](evidence/pr04/parameters.md),
проверки — в [evidence/pr04/tests.txt](evidence/pr04/tests.txt).

```bash
python3 -m pytest src/patrol/test -q
colcon test --packages-select patrol turtle_bringup
colcon test-result --verbose
python3 .course-kit/v1/tools/check_practice.py PR04 --submission .
```

Для checker нужен комплект курса `v1-w04`, SHA-256 архива
`fec6b4e886c19146078bf69fbf90a19279a4cd33f656642395350b299efeb226`.

## ПР03. Первая нода: поза и команда

Ветка `pr03` продолжает ПР02. Пакет `turtle_bringup` запускает готовый
симулятор, а новый пакет `patrol` содержит собственную ноду: она подписывается
на `/turtle1/pose` и раз в 0,1 с публикует команду скорости `Twist` в
относительный топик `cmd_vel`. До первой позы команда нулевая. После её
получения `linear.x=0.5`, `angular.z=0.3`; остальные поля остаются нулевыми.

Из корня репозитория в терминале A:

```bash
source /opt/ros/lyrical/setup.bash
export ROS_DOMAIN_ID=87
colcon build --symlink-install --packages-select turtle_bringup patrol
source install/setup.bash
ros2 launch turtle_bringup sim.launch.py
```

В терминале B с теми же `source` и `ROS_DOMAIN_ID` сначала проверьте ошибочную
связь командой `ros2 run patrol patrol`: относительное `cmd_vel` разрешается
как `/cmd_vel`, а turtlesim слушает `/turtle1/cmd_vel`. Остановите ноду
Ctrl+C и повторите запуск с исправлением имени:

```bash
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

В терминале C можно сравнить `ros2 topic info /cmd_vel --verbose` и
`ros2 topic info /turtle1/cmd_vel --verbose`, прочитать
`ros2 topic echo /turtle1/pose --once` и измерить частоту
`ros2 topic hz /turtle1/cmd_vel` примерно за 10 секунд. Протокол и
результаты находятся в [evidence/pr03/demo.md](evidence/pr03/demo.md) и
[evidence/pr03/tests.txt](evidence/pr03/tests.txt).

Проверка из корня:

```bash
python3 -m pytest src/patrol/test -q
colcon test --packages-select patrol turtle_bringup
colcon test-result --verbose
python3 .course-kit/v1/tools/check_practice.py PR03 --submission .
```

`check_practice.py` использует официальный комплект курса `v1-w03` с
SHA-256 `7fbfd3e8161ab6c6ebefc7663efdaf77d9a7d490399743507f33dcefbd5ac522`.

## ПР02. Терминал, пакет и запуск turtlesim

Ветка `pr02` продолжает [первую работу](evidence/pr01/graph.md). Здесь создан
пустой ROS 2 пакет `turtle_bringup`, добавлен launch-файл для готовой ноды
`turtlesim_node` и проведён CLI-опыт с правильным и ошибочным топиком скорости.

- [Команды, измерения и объяснение сбоя](evidence/pr02/commands.md)
- [Типы сообщений](evidence/pr02/types.md)
- [Машиночитаемый отчёт](evidence/pr02/report.json)
- [Использование ИИ](AI_USAGE.md)

## Среда и запуск

Работа выполнена на ROS 2 Lyrical в отдельном домене `87`. Для запуска без окна
использован `QT_QPA_PLATFORM=offscreen`; движение проверено сообщениями Pose.
Если нужна видимая черепаха, запускайте те же команды в графической среде без
этой переменной. Во всех терминалах используйте один `ROS_DOMAIN_ID`.

Из корня репозитория:

```bash
source /opt/ros/lyrical/setup.bash
export ROS_DOMAIN_ID=87
colcon build --symlink-install --packages-select turtle_bringup
source install/setup.bash
ros2 pkg prefix turtle_bringup
ros2 launch turtle_bringup sim.launch.py
```

В другом терминале с тем же ROS и доменом:

```bash
ros2 node list --no-daemon --spin-time 2
ros2 topic echo /turtle1/pose --once
ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
ros2 topic echo /turtle1/pose --once
```

Для воспроизведения сбоя запустите непрерывную публикацию в `/cmd_vel`, затем
сравните `ros2 topic info /cmd_vel --verbose` и
`ros2 topic info /turtle1/cmd_vel --verbose`. Остановите издателя Ctrl+C и
повторите с именем `/turtle1/cmd_vel`. Подробные команды и фактические выводы
есть в [протоколе](evidence/pr02/commands.md).

Проверки пакета и комплекта курса:

```bash
python3 -m py_compile src/turtle_bringup/launch/sim.launch.py
(cd src/turtle_bringup && python3 -m pytest test -q)
python3 .course-kit/pr02/v1/tools/check_practice.py PR02 --submission .
```

Последняя команда требует комплект `v1-w02` с SHA-256
`5d210c431e32418f45e2cffa9dd2028116c7a9520a36f3c7079c778cd73437a8`.
В CI он скачивается и проверяется автоматически.
