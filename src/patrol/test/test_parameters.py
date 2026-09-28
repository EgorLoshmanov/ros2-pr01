"""Check parameter updates on the actual ROS node."""

from patrol.patrol import Patrol
import rclpy
from rclpy.parameter import Parameter


def test_frequency_update_keeps_one_timer_and_rejects_bad_values() -> None:
    """A failed update preserves the setting and the running timer."""
    rclpy.init()
    node = Patrol()
    try:
        original_timer = node.command_timer
        result = node.set_parameters_atomically([
            Parameter('publish_hz', value=5.0),
        ])
        assert result.successful
        assert node.publish_hz == 5.0
        assert node.get_parameter('publish_hz').value == 5.0
        assert node.command_timer is not original_timer
        assert len(list(node.timers)) == 1
        assert node.command_timer.timer_period_ns == 200_000_000

        active_timer = node.command_timer
        for value in (0.0, -1.0, float('nan')):
            result = node.set_parameters_atomically([
                Parameter('publish_hz', value=value),
            ])
            assert not result.successful
            assert node.publish_hz == 5.0
            assert node.get_parameter('publish_hz').value == 5.0
            assert node.command_timer is active_timer
            assert len(list(node.timers)) == 1

        result = node.set_parameters_atomically([
            Parameter('linear_speed', value=0.8),
            Parameter('publish_hz', value=0.0),
        ])
        assert not result.successful
        assert node.linear_speed == 0.5
        assert node.publish_hz == 5.0
        assert node.command_timer is active_timer
    finally:
        node.destroy_node()
        rclpy.shutdown()
