"""Verify delivery across the relay's actual ROS QoS endpoints."""

from time import monotonic

from course_bringup.pose_relay import PoseRelay

import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy

from turtlesim_msgs.msg import Pose


def test_best_effort_receives_while_reliable_does_not(monkeypatch):
    """Exercise both subscriber profiles against one sensor publisher."""
    monkeypatch.setenv('ROS_DOMAIN_ID', '205')
    rclpy.init()
    relay = PoseRelay()
    probe = Node('pose_relay_test_probe')
    executor = SingleThreadedExecutor()
    executor.add_node(relay)
    executor.add_node(probe)
    received_best_effort = []
    received_reliable = []
    source = probe.create_publisher(Pose, 'source_pose', 10)
    probe.create_subscription(
        Pose, 'sensor_pose', received_best_effort.append,
        QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT))
    probe.create_subscription(
        Pose, 'sensor_pose', received_reliable.append,
        QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE))
    pose = Pose()
    pose.x = 1.25
    try:
        deadline = monotonic() + 5.0
        while monotonic() < deadline and not received_best_effort:
            source.publish(pose)
            executor.spin_once(timeout_sec=0.05)
        assert received_best_effort
        assert received_best_effort[0].x == pose.x
        assert not received_reliable
    finally:
        executor.remove_node(probe)
        executor.remove_node(relay)
        probe.destroy_node()
        relay.destroy_node()
        executor.shutdown()
        rclpy.shutdown()
