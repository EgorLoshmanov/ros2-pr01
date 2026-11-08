"""Check command conversion and the single owner of normalized odometry."""

import math

from ackermann_msgs.msg import AckermannDriveStamped
from nav_msgs.msg import Odometry
import pytest

from course_simulation.drive_adapter import convert_drive
from course_simulation.odom_adapter import normalize_odometry, odometry_transform


def drive(speed=0.5, steering=0.0, stamp=10.0):
    command = AckermannDriveStamped()
    command.drive.speed = speed
    command.drive.steering_angle = steering
    command.header.stamp.sec = int(stamp)
    command.header.stamp.nanosec = round((stamp % 1) * 1e9)
    return command


def odometry():
    source = Odometry()
    source.header.frame_id = 'course_ackermann/odom'
    source.child_frame_id = 'course_ackermann/base_link'
    source.header.stamp.sec = 7
    source.header.stamp.nanosec = 123456789
    source.pose.pose.position.x = 2.5
    source.pose.pose.orientation.w = 1.0
    source.twist.twist.linear.x = 0.4
    source.pose.covariance[0] = 0.11
    source.twist.covariance[0] = 0.22
    return source


def test_straight_and_turning():
    straight, reason = convert_drive(drive(speed=0.6), 10.1)
    assert reason == ''
    assert straight.linear.x == pytest.approx(0.6)
    assert straight.angular.z == 0
    turning, reason = convert_drive(drive(speed=0.8, steering=0.2), 10.1)
    assert reason == ''
    assert turning.angular.z == pytest.approx(0.8 * math.tan(0.2) / 0.8)


def test_clamps_and_zero_speed_cannot_spin():
    clamped, _ = convert_drive(drive(speed=2.0, steering=0.9), 10.0)
    assert clamped.linear.x == 1.2
    assert clamped.angular.z == pytest.approx(1.2 * math.tan(0.45) / 0.8)
    stopped, _ = convert_drive(drive(speed=0.0, steering=0.4), 10.0)
    assert stopped.linear.x == stopped.angular.z == 0.0
    reverse, _ = convert_drive(drive(speed=-1.0, steering=-0.4), 10.0)
    assert reverse.linear.x == reverse.angular.z == 0.0


@pytest.mark.parametrize('command, now, reason', [
    (drive(stamp=9.0), 10.0, 'stale'),
    (drive(speed=float('nan')), 10.0, 'non_finite'),
    (drive(steering=float('inf')), 10.0, 'non_finite'),
])
def test_rejected_command_is_zero(command, now, reason):
    twist, actual_reason = convert_drive(command, now)
    assert actual_reason == reason
    assert twist.linear.x == twist.angular.z == 0.0


def test_normalized_odometry_preserves_data_and_tf():
    source = odometry()
    result = normalize_odometry(source)
    assert result is not None
    assert (result.header.frame_id, result.child_frame_id) == ('odom', 'base_link')
    assert source.header.frame_id == 'course_ackermann/odom'
    assert result.header.stamp == source.header.stamp
    assert result.pose == source.pose
    assert result.twist == source.twist
    transform = odometry_transform(result)
    assert transform.header == result.header
    assert transform.child_frame_id == 'base_link'
    assert transform.transform.translation.x == 2.5
    assert transform.transform.rotation == result.pose.pose.orientation


@pytest.mark.parametrize('change', [
    lambda msg: setattr(msg.header, 'frame_id', 'other/odom'),
    lambda msg: setattr(msg, 'child_frame_id', 'other/base_link'),
    lambda msg: setattr(msg.pose.pose.position, 'x', float('nan')),
    lambda msg: msg.pose.covariance.__setitem__(0, float('inf')),
    lambda msg: setattr(msg.twist.twist.angular, 'z', float('nan')),
])
def test_rejects_foreign_frames_and_non_finite_data(change):
    source = odometry()
    change(source)
    assert normalize_odometry(source) is None
