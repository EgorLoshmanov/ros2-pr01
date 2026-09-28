"""Check velocity selection and parameter validation."""

from patrol.patrol import command_from_pose, validate_settings
import pytest
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


def test_pose_uses_current_speeds() -> None:
    """A received pose enables the supplied motion settings."""
    command = command_from_pose(Pose(), 0.8, -0.4)

    assert command.linear.x == 0.8
    assert command.angular.z == -0.4


@pytest.mark.parametrize('publish_hz', [10.0, 5.0, 1.0, 30.0])
def test_valid_frequency(publish_hz: float) -> None:
    """The original and updated rates fit the allowed interval."""
    validate_settings(0.5, 0.3, publish_hz)


@pytest.mark.parametrize('publish_hz', [0.0, -1.0, float('nan')])
def test_invalid_frequency(publish_hz: float) -> None:
    """Zero, negative, and NaN rates cannot become active."""
    with pytest.raises(ValueError, match='publish_hz'):
        validate_settings(0.5, 0.3, publish_hz)


@pytest.mark.parametrize('linear_speed, turn_rate', [
    (-0.1, 0.3), (1.1, 0.3), (0.5, -1.1), (0.5, 1.1),
    (float('inf'), 0.3), (0.5, float('nan')),
])
def test_invalid_motion_settings(linear_speed: float, turn_rate: float) -> None:
    """Every speed and turn value must be finite and in range."""
    with pytest.raises(ValueError):
        validate_settings(linear_speed, turn_rate, 10.0)
