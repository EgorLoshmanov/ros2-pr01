"""Launch one turtle with namespaced patrol and QoS demonstration nodes."""

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument, ExecuteProcess, GroupAction, LogInfo,
)
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node, PushRosNamespace


def generate_launch_description():
    """Build the complete system and optionally record its sensor topic."""
    namespace = LaunchConfiguration('namespace')
    record = LaunchConfiguration('record')
    bag_dir = LaunchConfiguration('bag_dir')
    subscriber_reliability = LaunchConfiguration('subscriber_reliability')
    sensor_topic = ['/', namespace, '/sensor_pose']

    return LaunchDescription([
        DeclareLaunchArgument('namespace', default_value='robot_a'),
        DeclareLaunchArgument('record', default_value='false'),
        DeclareLaunchArgument('bag_dir', default_value='evidence/pr05/bag'),
        DeclareLaunchArgument(
            'subscriber_reliability', default_value='best_effort'),
        LogInfo(msg=['Starting turtlesim and patrol in /', namespace]),
        Node(
            package='turtlesim', executable='turtlesim_node',
            output='screen'),
        GroupAction([
            PushRosNamespace(namespace),
            Node(
                package='patrol', executable='patrol', output='screen',
                remappings=[('pose', '/turtle1/pose'),
                            ('cmd_vel', '/turtle1/cmd_vel')]),
            Node(
                package='course_bringup', executable='pose_relay',
                output='screen',
                remappings=[('source_pose', '/turtle1/pose')]),
            Node(
                package='course_bringup', executable='pose_monitor',
                output='screen',
                parameters=[{'reliability': subscriber_reliability}]),
        ]),
        ExecuteProcess(
            cmd=['ros2', 'bag', 'record', '-s', 'mcap', '-o', bag_dir,
                 '--topics', sensor_topic],
            output='screen', condition=IfCondition(record)),
    ])
