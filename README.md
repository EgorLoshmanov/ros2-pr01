# ПР03. Первая нода: поза и команда

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
