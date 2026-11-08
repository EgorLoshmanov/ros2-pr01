"""Normalize Gazebo odometry and own the dynamic odom-to-base transform."""

from copy import deepcopy
import math

from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from tf2_ros import TransformBroadcaster


ODOM_QOS = QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)


def normalize_odometry(source: Odometry) -> Odometry | None:
    """Accept only the course model's finite odometry and remove its frame prefix."""
    if (source.header.frame_id != 'course_ackermann/odom'
            or source.child_frame_id != 'course_ackermann/base_link'):
        return None
    position = source.pose.pose.position
    orientation = source.pose.pose.orientation
    linear = source.twist.twist.linear
    angular = source.twist.twist.angular
    values = (
        position.x, position.y, position.z,
        orientation.x, orientation.y, orientation.z, orientation.w,
        linear.x, linear.y, linear.z, angular.x, angular.y, angular.z,
        *source.pose.covariance, *source.twist.covariance,
    )
    if not all(math.isfinite(value) for value in values):
        return None
    result = deepcopy(source)
    result.header.frame_id = 'odom'
    result.child_frame_id = 'base_link'
    return result


def odometry_transform(odom: Odometry) -> TransformStamped:
    """Build tf from the same stamp and pose as the normalized odometry."""
    transform = TransformStamped()
    transform.header = deepcopy(odom.header)
    transform.child_frame_id = odom.child_frame_id
    transform.transform.translation.x = odom.pose.pose.position.x
    transform.transform.translation.y = odom.pose.pose.position.y
    transform.transform.translation.z = odom.pose.pose.position.z
    transform.transform.rotation = deepcopy(odom.pose.pose.orientation)
    return transform


class OdomAdapter(Node):
    """Publish normalized odometry and its single dynamic transform."""

    def __init__(self):
        super().__init__('odom_adapter')
        self.declare_parameter('source_topic', '/vehicle/odom_gz')
        self.declare_parameter('odom_topic', '/vehicle/odom')
        self.publisher = self.create_publisher(
            Odometry, self.get_parameter('odom_topic').value, ODOM_QOS)
        self.transform_broadcaster = TransformBroadcaster(self)
        self.create_subscription(
            Odometry, self.get_parameter('source_topic').value, self.on_odometry, ODOM_QOS)

    def on_odometry(self, source: Odometry):
        odom = normalize_odometry(source)
        if odom is None:
            self.get_logger().warning('Rejected odometry: unexpected frames or non-finite value')
            return
        self.publisher.publish(odom)
        self.transform_broadcaster.sendTransform(odometry_transform(odom))


def main(args=None):
    rclpy.init(args=args)
    node = OdomAdapter()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
