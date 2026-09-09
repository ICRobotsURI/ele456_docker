from setuptools import setup

package_name = 'my_package'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Paolo',
    maintainer_email='pstegagno@uri.edu',
    description='Foundations for Robotics - Student package',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'my_node = my_package.my_node:main',
            'talker = my_package.my_publisher:main',
            'listener = my_package.my_subscriber:main',
            'example_cmd_vel = my_package.example_cmd_vel:main',
            'example_read_lidar = my_package.example_read_lidar:main',
            'example_cmd_vel_lidar = my_package.example_cmd_vel_lidar:main',
            'example_feedbacklin_controller = my_package.example_feedbacklin_controller:main',
            'example_occupancy_grid = my_package.example_occupancy_grid:main',
            'grader_w1 = my_package.grader_w1:main',
            'grader_w2 = my_package.grader_w2:main',
        ],
    },
)
