"""Check velocity selection without starting a ROS graph."""

from patrol.patrol import command_from_pose
from turtlesim_msgs.msg import Pose


def test_no_pose_sends_zero_twist() -> None:
    """The turtle must not move before the first pose arrives."""
    command = command_from_pose(None)

    assert command.linear.x == 0.0
    assert command.linear.y == 0.0
    assert command.linear.z == 0.0
    assert command.angular.x == 0.0
    assert command.angular.y == 0.0
    assert command.angular.z == 0.0


def test_pose_enables_expected_command() -> None:
    """Any received pose enables the fixed PR03 motion command."""
    command = command_from_pose(Pose(x=5.0, y=5.0, theta=0.0))

    assert command.linear.x == 0.5
    assert command.angular.z == 0.3
    assert command.linear.y == 0.0
    assert command.linear.z == 0.0
    assert command.angular.x == 0.0
    assert command.angular.y == 0.0
