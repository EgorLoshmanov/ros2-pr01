from glob import glob

from setuptools import find_packages, setup


package_name = 'course_description'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/urdf', glob('urdf/*.urdf.xacro')),
        ('share/' + package_name + '/rviz', glob('rviz/*.rviz')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Egor Loshmanov',
    maintainer_email='e.loshmanov@g.nsu.ru',
    description='URDF/Xacro description of the course Ackermann robot',
    license='Apache-2.0',
    extras_require={'test': ['pytest']},
)
