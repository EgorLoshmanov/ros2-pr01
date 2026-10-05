"""Publish a parameterized turtle velocity command after receiving its pose."""

import math

from geometry_msgs.msg import Twist
from rcl_interfaces.msg import SetParametersResult
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.parameter import Parameter
from turtlesim_msgs.msg import Pose


def validate_settings(
    linear_speed: float, turn_rate: float, publish_hz: float,
) -> None:
    """Reject nonfinite or out-of-range motion settings before applying them."""
    for name, value, minimum, maximum in (
        ('linear_speed', linear_speed, 0.0, 1.0),
        ('turn_rate', turn_rate, -1.0, 1.0),
        ('publish_hz', publish_hz, 1.0, 30.0),
    ):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f'{name} must be a finite number')
        if not math.isfinite(value) or not minimum <= value <= maximum:
            raise ValueError(f'{name} must be finite and in [{minimum}, {maximum}]')


def command_from_pose(
    pose: Pose | None, linear_speed: float = 0.5, turn_rate: float = 0.3,
) -> Twist:
    """Choose a command using the latest pose, or stop until one arrives."""
    command = Twist()
    if pose is not None:
        command.linear.x = linear_speed
        command.angular.z = turn_rate
    return command


class Patrol(Node):
    """Remember the last turtle pose and publish configurable commands."""

    def __init__(self) -> None:
        """Create the ROS subscription, publisher, and timer."""
        super().__init__('patrol')
        self.last_pose: Pose | None = None
        self.linear_speed = self.declare_parameter('linear_speed', 0.5).value
        self.turn_rate = self.declare_parameter('turn_rate', 0.3).value
        self.publish_hz = self.declare_parameter('publish_hz', 10.0).value
        validate_settings(self.linear_speed, self.turn_rate, self.publish_hz)
        self.pose_subscription = self.create_subscription(
            Pose, 'pose', self.remember_pose, 10)
        self.command_publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.command_timer = self.create_timer(
            1.0 / self.publish_hz, self.publish_command)
        self.add_on_set_parameters_callback(self.set_motion_parameters)

    def set_motion_parameters(
        self, parameters: list[Parameter],
    ) -> SetParametersResult:
        """Validate a whole update before changing active settings or timer."""
        changes = {parameter.name: parameter.value for parameter in parameters}
        linear_speed = changes.get('linear_speed', self.linear_speed)
        turn_rate = changes.get('turn_rate', self.turn_rate)
        publish_hz = changes.get('publish_hz', self.publish_hz)
        try:
            validate_settings(linear_speed, turn_rate, publish_hz)
        except ValueError as error:
            return SetParametersResult(successful=False, reason=str(error))

        if publish_hz != self.publish_hz:
            new_timer = self.create_timer(1.0 / publish_hz, self.publish_command)
            self.destroy_timer(self.command_timer)
            self.command_timer = new_timer
        self.linear_speed = linear_speed
        self.turn_rate = turn_rate
        self.publish_hz = publish_hz
        return SetParametersResult(successful=True)

    def remember_pose(self, pose: Pose) -> None:
        """Keep the latest pose without publishing in the callback."""
        self.last_pose = pose

    def publish_command(self) -> None:
        """Publish one command on each timer tick."""
        self.command_publisher.publish(command_from_pose(
            self.last_pose, self.linear_speed, self.turn_rate))


def main(args: list[str] | None = None) -> None:
    """Start ROS, spin until interrupted, and release node resources."""
    rclpy.init(args=args)
    node = Patrol()
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
