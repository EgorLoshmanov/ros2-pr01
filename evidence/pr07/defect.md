# Опыт с ошибочным топиком IMU

От коммита реализации `48f2d9961b4efb017697fc1907ed5c335f493c2f`
создана локальная ветка `pr07-defect`, коммит
`e7a588d33ffcce901ca0dee15c3b9d2f45072dd3`. В копии bridge YAML
`gz_topic_name` IMU заменён на `/vehicle/imu_typo`, остальные пары оставлены.

В дефектной ветке тот же тест маршрута дал `1 failed, 1 passed`
(`defect-test.txt`). В живом запуске `ros2 topic info -v /vehicle/imu`
показывал одного ROS-издателя `gazebo_bridge` с `BEST_EFFORT`, но
`timeout 3s ros2 topic echo /vehicle/imu --once --qos-reliability best_effort`
завершился кодом 124 без сообщения. `gz topic -i -t /vehicle/imu` показывал
издателя Gazebo, а `gz topic -e -t /vehicle/imu` выдал сообщение со stamp
и `frame_id=imu_link`. Точный вывод — в `defect-runtime.txt`.

После остановки единого launch выполнен `git switch pr07`. Тот же тест прошёл
(`2 passed`), а исправленный launch с одним мостом доставил сообщение IMU
в ROS со stamp и `frame_id=imu_link` (`fixed-test.txt`, `fixed-runtime.txt`).
Причина — опечатка имени источника в YAML, а не QoS или отсутствие ROS-издателя.
