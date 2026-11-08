"""Run one Gazebo server, one bridge, robot description, and both adapters."""

import os
from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction, SetEnvironmentVariable
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def gazebo_server(context):
    headless = LaunchConfiguration('headless').perform(context).lower() in ('true', '1', 'yes')
    command = ['gz', 'sim', '-s', '-r']
    if headless:
        command.append('--headless-rendering')
    command.append(LaunchConfiguration('world').perform(context))
    return [ExecuteProcess(cmd=command, output='screen')]


def generate_launch_description():
    share = Path(get_package_share_directory('course_simulation'))
    description_share = Path(get_package_share_directory('course_description'))
    xacro = description_share / 'urdf' / 'vehicle.urdf.xacro'
    model_path = str(share / 'models')
    inherited_path = os.environ.get('GZ_SIM_RESOURCE_PATH', '')
    resource_path = model_path + (':' + inherited_path if inherited_path else '')
    namespace = LaunchConfiguration('namespace')
    description = ParameterValue(Command(['xacro ', str(xacro)]), value_type=str)
    return LaunchDescription([
        DeclareLaunchArgument('world', default_value=str(share / 'worlds' / 'mcity-minimal.sdf')),
        DeclareLaunchArgument('bridge_config', default_value=str(share / 'config' / 'bridge.yaml')),
        DeclareLaunchArgument('headless', default_value='true'),
        DeclareLaunchArgument('namespace', default_value=''),
        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', resource_path),
        OpaqueFunction(function=gazebo_server),
        Node(
            package='robot_state_publisher', executable='robot_state_publisher',
            name='robot_state_publisher', namespace=namespace, output='screen',
            parameters=[{'robot_description': description, 'use_sim_time': True}],
            remappings=[('tf', '/tf'), ('tf_static', '/tf_static')],
        ),
        Node(
            package='ros_gz_bridge', executable='parameter_bridge', name='gazebo_bridge',
            namespace=namespace, output='screen',
            parameters=[{'config_file': LaunchConfiguration('bridge_config'), 'use_sim_time': True}],
        ),
        Node(
            package='course_simulation', executable='drive_adapter', name='drive_adapter',
            namespace=namespace, output='screen', parameters=[{'use_sim_time': True}],
        ),
        Node(
            package='course_simulation', executable='odom_adapter', name='odom_adapter',
            namespace=namespace, output='screen', parameters=[{'use_sim_time': True}],
            remappings=[('tf', '/tf')],
        ),
    ])
