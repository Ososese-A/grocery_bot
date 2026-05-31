import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'my_robot_store'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'images'), glob('images/*.jpeg')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ros_2',
    maintainer_email='ros_2@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'manager = my_robot_store.task_manager:main',
            'web_app = my_robot_store.web_bridge:main',
            'interaction = my_robot_store.interaction_sim:main',
            'vision = my_robot_store.vision:main',
        ],
    },
)
