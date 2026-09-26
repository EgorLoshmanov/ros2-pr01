# ПР03: первая нода, поза и команда

Опыт выполнен 26 сентября 2026 года на ROS 2 Lyrical с `ROS_DOMAIN_ID=87`.
`turtlesim` работал с `QT_QPA_PLATFORM=offscreen`: окно не показывалось, поэтому
движение проверено по топику позы. Пакет `turtle_bringup` из ПР02 сохранён;
новая нода находится в пакете `patrol`. Команда
`ros2 topic type /turtle1/pose` вернула `turtlesim_msgs/msg/Pose`
([исходный вывод](pose-type.txt)).

## Запуск

В корне репозитория:

```bash
source /opt/ros/lyrical/setup.bash
export ROS_DOMAIN_ID=87
colcon build --symlink-install --packages-select turtle_bringup patrol
source install/setup.bash
QT_QPA_PLATFORM=offscreen ros2 launch turtle_bringup sim.launch.py
```

Второй и третий терминалы используют те же `source` и `ROS_DOMAIN_ID`.
`ros2 node list --no-daemon --spin-time 2` показал `/turtlesim`
([вывод](nodes-running.txt)); начальная поза была
`(x=5.544445, y=5.544445, theta=0)` ([сообщение](pose-before.txt)).

## Разрыв имени

Во втором терминале запущено `ros2 run patrol patrol` без remap. Нода
`/patrol` появилась ([список нод](nodes-broken.txt)); команда `ros2 topic info
/cmd_vel --verbose` показала одного издателя и ноль подписчиков
([вывод](topic-broken.txt)). У правильного имени `/turtle1/cmd_vel` были ноль
издателей и один подписчик `turtlesim`
([вывод](topic-target-before-fix.txt)). Через две секунды поза осталась
`(5.544445, 5.544445, 0)` ([сообщение](pose-broken.txt)).

Причина: `cmd_vel` в корневом пространстве имён ноды разрешился в
`/cmd_vel`, а `turtlesim` подписан на другой топик — `/turtle1/cmd_vel`.
Совпадение типа `geometry_msgs/msg/Twist` не соединяет разные имена.

## Исправление и частота

После Ctrl+C нода запущена с remap:

```bash
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

`ros2 topic info /turtle1/cmd_vel --verbose` показала одного издателя и
одного подписчика ([вывод](topic-fixed.txt)). Поза изменилась до
`(6.805255, 6.125733, 0.8592)` при скоростях `0.5` и `0.3`
([сообщение](pose-fixed.txt)).

Частота измерена командой `ros2 topic hz /turtle1/cmd_vel --window 100`.
Последнее окно из 100 сообщений дало **9.999 Гц**; промежуточные окна и
интервалы приведены в [исходном выводе](command-hz.txt). CLI работал около
13 секунд, из них окно в 100 сообщений покрывает примерно 10 секунд.
Код `124` в файле означает штатное завершение измерения внешней командой
`timeout`, а не сбой ноды.

После остановки издателя Ctrl+C черепаха ещё немного изменила позу, затем
скорости стали нулевыми ([поза во время измерения](pose-after-hz.txt),
[поза после ожидания](pose-resting.txt)). Исчезновение издателя само по себе
не является мгновенной командой торможения. После Ctrl+C для launch список
нод пуст ([вывод](nodes-final.txt)); [журнал запуска](launch.txt) показывает
штатное завершение `turtlesim`.

## Роли частей ноды

`rclpy.init()` подключает программу к ROS 2. Подписка получает сообщения
`/turtle1/pose`; её callback только сохраняет последнюю позу. Таймер раз в
0,1 с вызывает отдельный callback, который публикует `Twist`. До первой позы
он публикует нули; после неё — `linear.x=0.5` и `angular.z=0.3`.
`rclpy.spin()` обслуживает подписку и таймер, пока нода работает. Ctrl+C
прерывает `spin`; программа уничтожает ноду и завершает работу с ROS.

Проверки собраны в [tests.txt](tests.txt). Графический маршрут мышью из
необязательного раздела задания в эту работу не включён.
