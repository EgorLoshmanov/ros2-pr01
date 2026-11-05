"""Наблюдать за позой с выбираемой надёжностью доставки QoS."""

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy

from turtlesim_msgs.msg import Pose


class PoseMonitor(Node):
    """Вывести первую полученную позу, чтобы проверить доставку."""

    def __init__(self) -> None:
        """Настроить подписку по значению параметра ROS."""
        super().__init__('pose_monitor')
        # Launch может заменить стандартное значение параметра reliability.
        reliability = self.declare_parameter(
            'reliability', 'best_effort').value
        # Преобразуем текст параметра в политику QoS библиотеки rclpy.
        policies = {
            'best_effort': ReliabilityPolicy.BEST_EFFORT,
            'reliable': ReliabilityPolicy.RELIABLE,
        }
        if reliability not in policies:
            raise ValueError('reliability must be best_effort or reliable')
        # Выбранная политика определяет совместимость с издателем relay.
        qos = QoSProfile(depth=10, reliability=policies[reliability])
        self.received = 0
        # В namespace robot_a это подписка на /robot_a/sensor_pose.
        self.subscription = self.create_subscription(
            Pose, 'sensor_pose', self.on_pose, qos)
        self.get_logger().info(f'Listening to sensor_pose ({reliability})')

    def on_pose(self, pose: Pose) -> None:
        """Посчитать полученную позу и вывести координаты только первой."""
        self.received += 1
        if self.received == 1:
            # Не печатаем каждую следующую позу, чтобы не засорять журнал.
            self.get_logger().info(
                f'First sensor_pose received: x={pose.x:.3f}, y={pose.y:.3f}')


def main(args: list[str] | None = None) -> None:
    """Запустить monitor и корректно освободить ресурсы при остановке."""
    rclpy.init(args=args)
    node = PoseMonitor()
    try:
        # spin вызывает on_pose при доставке сообщения подписчику.
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
