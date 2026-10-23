"""Publish the course vehicle's fixed and optional moving transforms."""

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from pathlib import Path


def generate_launch_description():
    share = Path(get_package_share_directory('course_description'))
    xacro_file = share / 'urdf' / 'vehicle.urdf.xacro'
    description = ParameterValue(Command(['xacro ', str(xacro_file)]), value_type=str)
    return LaunchDescription([
        DeclareLaunchArgument('rviz', default_value='false', description='Open RViz'),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': description}],
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', str(share / 'rviz' / 'vehicle.rviz')],
            condition=IfCondition(LaunchConfiguration('rviz')),
        ),
    ])
