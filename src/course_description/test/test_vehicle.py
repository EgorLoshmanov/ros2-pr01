"""Check the expanded robot tree and its dimensions."""

from pathlib import Path
import math
import subprocess
import xml.etree.ElementTree as ET

import pytest


XACRO = Path(__file__).resolve().parents[1] / 'urdf' / 'vehicle.urdf.xacro'


@pytest.fixture(scope='module')
def robot():
    result = subprocess.run(['xacro', str(XACRO)], capture_output=True, text=True, check=True)
    return ET.fromstring(result.stdout)


def test_tree_and_unique_transform_owners(robot):
    links = {link.attrib['name'] for link in robot.findall('link')}
    joints = robot.findall('joint')
    children = [joint.find('child').attrib['link'] for joint in joints]
    assert len(links) == 10
    assert len(joints) == 9
    assert len(children) == len(set(children))
    assert set(children) == links - {'base_link'}
    parents = {joint.find('child').attrib['link']: joint.find('parent').attrib['link'] for joint in joints}
    for child in children:
        visited = set()
        while child != 'base_link':
            assert child not in visited
            visited.add(child)
            child = parents[child]


@pytest.mark.parametrize('child', ['camera_link', 'lidar_link', 'imu_link'])
def test_sensor_parent_and_offset(robot, child):
    joint = next(j for j in robot.findall('joint') if j.find('child').attrib['link'] == child)
    assert joint.attrib['type'] == 'fixed'
    assert joint.find('parent').attrib['link'] == 'base_link'
    xyz = [float(n) for n in joint.find('origin').attrib['xyz'].split()]
    assert xyz == pytest.approx([0.28, 0.0, 0.38])


def test_wheel_geometry_and_placement(robot):
    joints = {j.attrib['name']: j for j in robot.findall('joint')}
    wheels = {l.attrib['name']: l for l in robot.findall('link') if l.attrib['name'].endswith('_wheel')}
    assert len(wheels) == 4
    for name, link in wheels.items():
        visual = link.find('visual/geometry/cylinder')
        collision = link.find('collision/geometry/cylinder')
        assert float(visual.attrib['radius']) == pytest.approx(0.12)
        assert float(collision.attrib['radius']) == pytest.approx(0.12)
        assert float(visual.attrib['length']) == pytest.approx(0.07)
        assert float(collision.attrib['length']) == pytest.approx(0.07)
        assert joints[name + '_joint'].find('axis').attrib['xyz'] == '0 1 0'
    for side, sign in [('left', 1), ('right', -1)]:
        front = joints[f'front_{side}_steering_joint']
        rear = joints[f'rear_{side}_wheel_joint']
        assert [float(x) for x in front.find('origin').attrib['xyz'].split()] == pytest.approx([0.4, sign * 0.31, 0])
        assert [float(x) for x in rear.find('origin').attrib['xyz'].split()] == pytest.approx([-0.4, sign * 0.31, 0])


def test_geometry_and_inertia_are_valid(robot):
    for link in robot.findall('link'):
        visual = link.find('visual')
        collision = link.find('collision')
        if visual is not None:
            assert visual.find('geometry') is not None
            assert collision is not None and collision.find('geometry') is not None
        inertial = link.find('inertial')
        assert inertial is not None
        mass = float(inertial.find('mass').attrib['value'])
        inertia = inertial.find('inertia').attrib
        diagonal = [float(inertia[key]) for key in ('ixx', 'iyy', 'izz')]
        assert math.isfinite(mass) and mass > 0
        assert all(math.isfinite(x) and x > 0 for x in diagonal)
        assert all(diagonal[i] <= sum(diagonal) - diagonal[i] + 1e-9 for i in range(3))
