"""Observe the relayed pose using a configurable reliability policy."""

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy

from turtlesim_msgs.msg import Pose


class PoseMonitor(Node):
    """Log the first sensor pose received with the requested QoS."""

    def __init__(self) -> None:
        """Configure the subscription from a ROS parameter."""
        super().__init__('pose_monitor')
        reliability = self.declare_parameter(
            'reliability', 'best_effort').value
        policies = {
            'best_effort': ReliabilityPolicy.BEST_EFFORT,
            'reliable': ReliabilityPolicy.RELIABLE,
        }
        if reliability not in policies:
            raise ValueError('reliability must be best_effort or reliable')
        qos = QoSProfile(depth=10, reliability=policies[reliability])
        self.received = 0
        self.subscription = self.create_subscription(
            Pose, 'sensor_pose', self.on_pose, qos)
        self.get_logger().info(f'Listening to sensor_pose ({reliability})')

    def on_pose(self, pose: Pose) -> None:
        """Report the first delivered pose as a visible delivery check."""
        self.received += 1
        if self.received == 1:
            self.get_logger().info(
                f'First sensor_pose received: x={pose.x:.3f}, y={pose.y:.3f}')


def main(args: list[str] | None = None) -> None:
    """Run the monitor until ROS shuts down."""
    rclpy.init(args=args)
    node = PoseMonitor()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
