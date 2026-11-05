"""Пересылать позу черепахи в топик датчика с QoS best_effort."""

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy

from turtlesim_msgs.msg import Pose


class PoseRelay(Node):
    """Копировать позу из топика симулятора в относительный топик."""

    def __init__(self) -> None:
        """Создать подписку на исходную позу и издателя позы датчика."""
        super().__init__('pose_relay')
        # Для выходящего потока задаём очередь на 10 поз и best_effort.
        sensor_qos = QoSProfile(
            depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        # В namespace robot_a относительное имя станет /robot_a/sensor_pose.
        self.publisher = self.create_publisher(Pose, 'sensor_pose', sensor_qos)
        # Launch переназначает source_pose на глобальный /turtle1/pose.
        # Каждую полученную Pose сразу передаём методу publish без изменений.
        self.subscription = self.create_subscription(
            Pose, 'source_pose', self.publisher.publish, 10)
        self.get_logger().info(
            'Relaying source_pose to sensor_pose (best_effort)')


def main(args: list[str] | None = None) -> None:
    """Запустить relay и корректно освободить ресурсы при остановке."""
    rclpy.init(args=args)
    node = PoseRelay()
    try:
        # spin вызывает обработчик подписки при поступлении каждой позы.
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        # Удаляем ноду и завершаем ROS, если он ещё работает.
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
