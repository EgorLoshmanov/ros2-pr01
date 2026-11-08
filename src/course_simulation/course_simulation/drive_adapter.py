"""Translate fresh safe Ackermann commands to Gazebo's Twist input."""

import math

from ackermann_msgs.msg import AckermannDriveStamped
from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from std_msgs.msg import String


MAX_AGE_SECONDS = 0.25
WHEEL_BASE_METERS = 0.8
COMMAND_QOS = QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)


def convert_drive(command: AckermannDriveStamped, now_seconds: float) -> tuple[Twist, str]:
    """Return a Twist and an empty reason for a valid command, or zero and a reason."""
    twist = Twist()
    speed = command.drive.speed
    steering = command.drive.steering_angle
    if not all(math.isfinite(value) for value in (speed, steering, now_seconds)):
        return twist, 'non_finite'
    stamp = command.header.stamp.sec + command.header.stamp.nanosec * 1e-9
    if now_seconds - stamp > MAX_AGE_SECONDS:
        return twist, 'stale'
    velocity = min(max(speed, 0.0), 1.2)
    angle = min(max(steering, -0.45), 0.45)
    twist.linear.x = velocity
    twist.angular.z = velocity * math.tan(angle) / WHEEL_BASE_METERS
    return twist, ''


class DriveAdapter(Node):
    """Publish one Gazebo command for each safe command, including rejected ones."""

    def __init__(self):
        super().__init__('drive_adapter')
        self.declare_parameter('safe_topic', '/drive/safe')
        self.declare_parameter('gazebo_command_topic', '/vehicle/gz_cmd_vel')
        self.publisher = self.create_publisher(
            Twist, self.get_parameter('gazebo_command_topic').value, COMMAND_QOS)
        self.reason_publisher = self.create_publisher(
            String, '/vehicle/drive_reject_reason', COMMAND_QOS)
        self.create_subscription(
            AckermannDriveStamped, self.get_parameter('safe_topic').value,
            self.on_command, COMMAND_QOS)

    def on_command(self, command: AckermannDriveStamped):
        now = self.get_clock().now().nanoseconds * 1e-9
        twist, reason = convert_drive(command, now)
        self.publisher.publish(twist)
        if reason:
            self.reason_publisher.publish(String(data=reason))
            self.get_logger().warning(f'Rejected safe drive command: {reason}')


def main(args=None):
    rclpy.init(args=args)
    node = DriveAdapter()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
