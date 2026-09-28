# ПР04: параметры, сервис и действие

28 сентября 2026 года, ROS 2 Lyrical, `ROS_DOMAIN_ID=104`,
`QT_QPA_PLATFORM=offscreen`. Из корня репозитория собраны пакеты
`turtle_bringup` и `patrol`; в отдельных терминалах запущены
`ros2 launch turtle_bringup sim.launch.py` и
`ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel`.
Окно черепахи не показывалось; командный поток измерен через ROS.

```text
$ ros2 topic type /turtle1/pose
turtlesim_msgs/msg/Pose
$ ros2 param get /patrol publish_hz
Double value is: 10.0
$ ros2 topic hz /turtle1/cmd_vel --window 20
average rate: 9.999
    min: 0.097s max: 0.102s std dev: 0.00115s window: 20
$ ros2 param set /patrol publish_hz 5.0
Set parameter successful
$ ros2 topic hz /turtle1/cmd_vel --window 20
average rate: 5.002
    min: 0.196s max: 0.205s std dev: 0.00179s window: 20
$ ros2 param set /patrol publish_hz 0.0
Setting parameter failed: publish_hz must be finite and in [1.0, 30.0]
$ ros2 param get /patrol publish_hz
Double value is: 5.0
$ ros2 topic hz /turtle1/cmd_vel --window 20
average rate: 5.000
    min: 0.197s max: 0.203s std dev: 0.00207s window: 20
$ ros2 param set /patrol linear_speed 0.8
Set parameter successful
$ ros2 param set /patrol turn_rate -0.4
Set parameter successful
$ ros2 topic echo /turtle1/cmd_vel --once
linear:
  x: 0.8
  y: 0.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: -0.4
---
```

Отдельная ветка `pr04-defect`, коммит
`9f96f05b5b770a8b7987b5c4e4b44041a2975928`, временно пропускает
проверку `publish_hz`. Тот же тест передал `0.0` в параметр и получил
`ZeroDivisionError: division by zero` на `create_timer(1.0 / publish_hz)`:
недопустимое значение дошло до пересоздания таймера. В ветке `pr04`
проверка восстановлена; тест для нуля, отрицательного значения и NaN прошёл,
активный параметр и единственный таймер сохраняются при отказе.

```text
$ ros2 service call /clear std_srvs/srv/Empty '{}'
requester: making request: std_srvs.srv.Empty_Request()
response:
std_srvs.srv.Empty_Response()
$ ros2 action list -t
/turtle1/rotate_absolute [turtlesim_msgs/action/RotateAbsolute]
```

Запрос `/clear` вызывает готовый сервис один раз и получает один ответ.
Цель `/turtle1/rotate_absolute` запускает поворот, за которым клиент может
следить по feedback и затем получить результат или отменить цель.
