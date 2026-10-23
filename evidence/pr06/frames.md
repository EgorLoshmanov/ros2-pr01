# Системы координат ПР06

Модель `course_ackermann` развёрнута из `src/course_description/urdf/vehicle.urdf.xacro`. Оси REP-103: x вперёд, y влево, z вверх; расстояния в метрах, углы в радианах. Размеры из SDF: база 0.80, колея 0.62, радиус колеса 0.12. Корень дерева — `base_link`; `map` и `odom` пока не публикуются.

| Joint | Parent → child | Ожидаемый сдвиг xyz, поворот | Тип и владелец публикации |
| --- | --- | --- | --- |
| `camera_joint` | `base_link` → `camera_link` | `(0.28, 0, 0.38)`, нулевой | fixed, `robot_state_publisher` → `/tf_static` |
| `lidar_joint` | `base_link` → `lidar_link` | `(0.28, 0, 0.38)`, нулевой | fixed, `robot_state_publisher` → `/tf_static` |
| `imu_joint` | `base_link` → `imu_link` | `(0.28, 0, 0.38)`, нулевой | fixed, `robot_state_publisher` → `/tf_static` |
| `front_left_steering_joint` | `base_link` → `front_left_knuckle` | `(0.40, 0.31, 0)`, вокруг z | revolute, `robot_state_publisher` → `/tf` после `/joint_states` |
| `front_right_steering_joint` | `base_link` → `front_right_knuckle` | `(0.40, -0.31, 0)`, вокруг z | revolute, `robot_state_publisher` → `/tf` после `/joint_states` |
| `front_left_wheel_joint` | `front_left_knuckle` → `front_left_wheel` | `(0, 0, 0)`, вокруг y | continuous, `robot_state_publisher` → `/tf` после `/joint_states` |
| `front_right_wheel_joint` | `front_right_knuckle` → `front_right_wheel` | `(0, 0, 0)`, вокруг y | continuous, `robot_state_publisher` → `/tf` после `/joint_states` |
| `rear_left_wheel_joint` | `base_link` → `rear_left_wheel` | `(-0.40, 0.31, 0)`, вокруг y | continuous, `robot_state_publisher` → `/tf` после `/joint_states` |
| `rear_right_wheel_joint` | `base_link` → `rear_right_wheel` | `(-0.40, -0.31, 0)`, вокруг y | continuous, `robot_state_publisher` → `/tf` после `/joint_states` |

Все девять преобразований принадлежат одной ноде `robot_state_publisher`, запущенной из `description.launch.py`. Отдельного издателя `map → odom` или `odom → base_link` нет. Подвижные звенья не появляются в живом `/tf` до сообщения `/joint_states`; это ожидается без `joint_state_publisher`.

В ветке `pr06-defect` (`d626a8a249aca954fec76e62d133259610133358`) parent у `lidar_joint` заменён на `camera_link`, а локальный offset оставлен `(0.28, 0, 0.38)`. Поэтому `base_link → lidar_link` становится `(0.56, 0, 0.76)`. `check_urdf` принимает оба связных дерева, но тест `test_sensor_parent_and_offset[lidar_link]` обнаруживает неверную связь. Исправленная ветка `pr06` возвращает parent `base_link`.
