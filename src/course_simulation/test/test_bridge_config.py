"""Guard the bridge boundary that a typo can silently disconnect."""

from pathlib import Path

import yaml


CONFIG = Path(__file__).resolve().parents[1] / 'config' / 'bridge.yaml'


def test_command_and_imu_bridge_routes():
    routes = {item['ros_topic_name']: item for item in yaml.safe_load(CONFIG.read_text())}
    command = routes['/vehicle/gz_cmd_vel']
    assert command['gz_topic_name'] == '/model/course_ackermann/cmd_vel'
    assert command['direction'] == 'ROS_TO_GZ'
    imu = routes['/vehicle/imu']
    assert imu['gz_topic_name'] == '/vehicle/imu'
    assert imu['direction'] == 'GZ_TO_ROS'
    assert imu['qos_profile'] == 'SENSOR_DATA'


def test_odometry_is_bridged_only_to_adapter_input():
    routes = {item['ros_topic_name']: item for item in yaml.safe_load(CONFIG.read_text())}
    assert '/vehicle/odom' not in routes
    assert routes['/vehicle/odom_gz']['gz_topic_name'] == '/model/course_ackermann/odometry'
    assert routes['/vehicle/odom_gz']['direction'] == 'GZ_TO_ROS'
