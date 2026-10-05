"""Relay the turtlesim pose through a best-effort sensor topic."""

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy

from turtlesim_msgs.msg import Pose


class PoseRelay(Node):
    """Copy the global turtle pose to a relative, best-effort topic."""

    def __init__(self) -> None:
        """Create the source subscription and sensor publisher."""
        super().__init__('pose_relay')
        sensor_qos = QoSProfile(
            depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.publisher = self.create_publisher(Pose, 'sensor_pose', sensor_qos)
        self.subscription = self.create_subscription(
            Pose, 'source_pose', self.publisher.publish, 10)
        self.get_logger().info(
            'Relaying source_pose to sensor_pose (best_effort)')


def main(args: list[str] | None = None) -> None:
    """Run the relay until ROS shuts down."""
    rclpy.init(args=args)
    node = PoseRelay()
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
