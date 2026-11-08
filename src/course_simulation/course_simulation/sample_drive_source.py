"""Send short, freshly stamped safe commands for the PR07 live experiment."""

from ackermann_msgs.msg import AckermannDriveStamped
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy


class TestDriveSource(Node):
    """Use /clock for stamps and finish each experiment with a stop command."""

    def __init__(self):
        super().__init__('test_drive_source')
        self.declare_parameter('speed', 0.4)
        self.declare_parameter('steering_angle', 0.0)
        self.declare_parameter('duration', 4.0)
        self.publisher = self.create_publisher(
            AckermannDriveStamped, '/drive/safe',
            QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE))
        self.started_at = None
        self.timer = self.create_timer(0.1, self.tick)

    def tick(self):
        now = self.get_clock().now()
        if now.nanoseconds == 0:
            return
        if self.started_at is None:
            self.started_at = now
        elapsed = (now - self.started_at).nanoseconds * 1e-9
        command = AckermannDriveStamped()
        command.header.stamp = now.to_msg()
        if elapsed < self.get_parameter('duration').value:
            command.drive.speed = self.get_parameter('speed').value
            command.drive.steering_angle = self.get_parameter('steering_angle').value
        else:
            self.timer.cancel()
            self.get_logger().info('Sent final zero drive command')
        self.publisher.publish(command)


def main(args=None):
    rclpy.init(args=args)
    node = TestDriveSource()
    try:
        while rclpy.ok() and not node.timer.is_canceled():
            rclpy.spin_once(node, timeout_sec=0.5)
    finally:
        node.destroy_node()
        rclpy.shutdown()
