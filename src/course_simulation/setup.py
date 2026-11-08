from glob import glob

from setuptools import find_packages, setup


package_name = 'course_simulation'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
        ('share/' + package_name + '/models/course_ackermann', glob('models/course_ackermann/*')),
        ('share/' + package_name + '/worlds', glob('worlds/*.sdf')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Egor Loshmanov',
    maintainer_email='e.loshmanov@g.nsu.ru',
    description='Gazebo launch, Ackermann command, and odometry adapters',
    license='Apache-2.0',
    extras_require={'test': ['pytest']},
    entry_points={'console_scripts': [
        'drive_adapter = course_simulation.drive_adapter:main',
        'odom_adapter = course_simulation.odom_adapter:main',
        'test_drive_source = course_simulation.sample_drive_source:main',
    ]},
)
