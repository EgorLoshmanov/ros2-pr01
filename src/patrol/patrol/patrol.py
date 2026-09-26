"""Publish a turtle velocity command after receiving its pose."""

from geometry_msgs.msg import Twist
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from turtlesim_msgs.msg import Pose


def command_from_pose(pose: Pose | None) -> Twist:
    """Choose a command using the latest pose, or stop until one arrives."""
    command = Twist()
    if pose is not None:
        command.linear.x = 0.5
        command.angular.z = 0.3
    return command


class Patrol(Node):
    """Remember the last turtle pose and publish commands every 0.1 s."""

    def __init__(self) -> None:
        """Create the ROS subscription, publisher, and timer."""
        super().__init__('patrol')
        self.last_pose: Pose | None = None
        self.pose_subscription = self.create_subscription(
            Pose, '/turtle1/pose', self.remember_pose, 10)
        self.command_publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.command_timer = self.create_timer(0.1, self.publish_command)

    def remember_pose(self, pose: Pose) -> None:
        """Keep the latest pose without publishing in the callback."""
        self.last_pose = pose

    def publish_command(self) -> None:
        """Publish one command on each timer tick."""
        self.command_publisher.publish(command_from_pose(self.last_pose))


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
