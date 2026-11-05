"""Запустить черепаху, управление и ноды для опыта с QoS."""

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument, ExecuteProcess, GroupAction, LogInfo,
)
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node, PushRosNamespace


def generate_launch_description():
    """Описать запуск системы и необязательную запись поз в MCAP."""
    # LaunchConfiguration получает значение аргумента во время запуска.
    namespace = LaunchConfiguration('namespace')
    record = LaunchConfiguration('record')
    bag_dir = LaunchConfiguration('bag_dir')
    subscriber_reliability = LaunchConfiguration('subscriber_reliability')
    # Части имени объединятся в /robot_a/sensor_pose при стандартном namespace.
    sensor_topic = ['/', namespace, '/sensor_pose']

    return LaunchDescription([
        # Эти значения можно переопределить аргументами ros2 launch.
        DeclareLaunchArgument('namespace', default_value='robot_a'),
        DeclareLaunchArgument('record', default_value='false'),
        DeclareLaunchArgument('bag_dir', default_value='evidence/pr05/bag'),
        DeclareLaunchArgument(
            'subscriber_reliability', default_value='best_effort'),
        LogInfo(msg=['Starting turtlesim and patrol in /', namespace]),
        # Симулятор остаётся вне группы, поэтому его топики глобальные.
        Node(
            package='turtlesim', executable='turtlesim_node',
            output='screen'),
        GroupAction([
            # Следующие три ноды работают в пространстве имён /robot_a.
            PushRosNamespace(namespace),
            # Относительные имена patrol соединяем с топиками симулятора.
            Node(
                package='patrol', executable='patrol', output='screen',
                remappings=[('pose', '/turtle1/pose'),
                            ('cmd_vel', '/turtle1/cmd_vel')]),
            # relay читает позу черепахи и публикует sensor_pose.
            Node(
                package='course_bringup', executable='pose_relay',
                output='screen',
                remappings=[('source_pose', '/turtle1/pose')]),
            # monitor получает выбор QoS через параметр reliability.
            Node(
                package='course_bringup', executable='pose_monitor',
                output='screen',
                parameters=[{'reliability': subscriber_reliability}]),
        ]),
        # Процесс записи запускается только при record:=true.
        ExecuteProcess(
            cmd=['ros2', 'bag', 'record', '-s', 'mcap', '-o', bag_dir,
                 '--topics', sensor_topic],
            output='screen', condition=IfCondition(record)),
    ])
