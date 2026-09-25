# Типы сообщений в опыте ПР02

| Топик | Тип | Роль |
| --- | --- | --- |
| `/turtle1/cmd_vel` | `geometry_msgs/msg/Twist` | turtlesim принимает команду скорости |
| `/turtle1/pose` | `turtlesim_msgs/msg/Pose` | turtlesim публикует положение и скорость |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | ошибочное имя в опыте, без подписчика turtlesim |

Тип позы получен командой `ros2 topic type /turtle1/pose` и сохранён в
[pose-type.txt](pose-type.txt). Поля `Twist` сохранены в
[twist-interface.txt](twist-interface.txt); стороны соединения видны в
[topic-broken.txt](topic-broken.txt) и [topic-fixed.txt](topic-fixed.txt).

`Twist.linear` и `Twist.angular` — трёхмерные векторы. В опыте заданы только
`linear.x = 1.0` для движения вперёд и `angular.z = 0.5` для поворота против
часовой стрелки; остальные компоненты равны нулю. Это команда **скорости**, а
не целевых координат. У `Twist` нет метки времени или системы координат.

`Pose` содержит `x`, `y`, `theta`, `linear_velocity` и `angular_velocity`.
Изменение координат доказывает движение, а нулевые скорости после остановки
издателя подтверждают прекращение движения. В Lyrical тип позы называется
`turtlesim_msgs/msg/Pose`.
