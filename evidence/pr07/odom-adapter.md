# Одометрия и владельцы преобразований

Исходный bridge из course kit публиковал ROS-одометрию на `/vehicle/odom`.
В своей копии изменён только `ros_topic_name` этой пары на
`/vehicle/odom_gz`. Адаптер подписывается на него и принимает только
`header.frame_id=course_ackermann/odom` и
`child_frame_id=course_ackermann/base_link` с конечными числовыми полями.

Выход `/vehicle/odom` имеет `header.frame_id=odom` и
`child_frame_id=base_link`. `header.stamp`, `pose`, `twist` и обе матрицы
ковариации сохраняются. Это проверено тестом
`test_normalized_odometry_preserves_data_and_tf` в
`src/course_simulation/test/test_adapters.py`: stamp `7.123456789` остаётся
тем же в выходной одометрии и в `TransformStamped`.

Единственный динамический `odom→base_link` публикует `odom_adapter` через
`TransformBroadcaster` из той же нормализованной позы и stamp. Фиксированные
`base_link→camera_link`, `base_link→lidar_link`, `base_link→imu_link`
публикует `robot_state_publisher` из ПР06 в `/tf_static`. Gazebo-топик
`/model/course_ackermann/tf` не переносится в ROS. В живом опыте после
движения `/vehicle/odom` дал `(3.692, 1.276, 0)`, а `tf2_echo odom base_link`
показал те же координаты; полный вывод — в `motion.txt`.

MCAP содержит нормализованную `/vehicle/odom`, `/tf` и `/tf_static`. При
воспроизведении записи в ПР08 адаптер одометрии повторно не запускается.
