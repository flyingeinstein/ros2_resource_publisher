##!/usr/bin/env python3

""" Publishes a resource (file) to a latching topic """

# sample arguments:
# -package lss_humanoid -xacro urdf/lss_humanoid.xacro.urdf 

import argparse
import os
import sys
import psutil

# Ros2 imports
import rclpy
import xacro
from launch.event_handlers import OnProcessIO
from rclpy.node import Node
from ament_index_python.packages import PackageNotFoundError, get_package_share_directory
from std_msgs.msg import String
from rclpy.qos import QoSProfile, QoSDurabilityPolicy


class ResourcePublisherNode(Node):
    package_dir = None
    xacro_urdf_file = None

    # list of publishers we create
    targets = None
    publishers = []

    def __init__(self, args, targets=None):
        super().__init__('resource_publisher')
        self.targets = targets

        parser = argparse.ArgumentParser(
            description='Publish a file to a Ros2 topic')
        parser.add_argument('-package', required=True, type=str, metavar='PKG_NAME',
                            help='The package containing the resource')
        parser.add_argument('-xacro', required=True, type=str, metavar='FILE_NAME',
                            help='The xacro file to substitute with parameters')
        parser.add_argument('-topic', type=str, metavar='TOPIC_NAME',
                            help='topic to publish on. Target name will also be appended if set.')
        parser.add_argument('-targets', type=str, default='*',
                            help='Comma-seperated list of targets. Each value will be passed '
                                 'to the xacro file as a "target" parameter and published '
                                 'on a new topic. Use * for <unset> target.')
        self.args = parser.parse_args(args[1:])

        # parse targets
        if not self.targets and self.args.targets:
            print(self.args.targets)
            self.targets = [arg.strip() for arg in self.args.targets.split(',')]
            print(self.targets)

        # create the latching QoS for our topics
        self.qos = QoSProfile(
            depth=1,
            #durability=QoSDurabilityPolicy.RMW_QOS_POLICY_DURABILITY_TRANSIENT_LOCAL
            durability = QoSDurabilityPolicy.TRANSIENT_LOCAL
        )

        # get the share location for the package containing the model
        # we will be training
        try:
            self.package_dir = get_package_share_directory(self.args.package)
            self.xacro_urdf_file = os.path.join(
                self.package_dir,
                self.args.xacro
            )
            self.get_logger().info(f'using xacro urdf file at {self.xacro_urdf_file}')
        except PackageNotFoundError as e:
            self.get_logger().error(f'cannot find share folder for package {self.args.package}')
            exit(-2)

        # change directory to the URDF file since xacro can error on relative includes
        self.start_cwd = os.getcwd()
        absolute_urdf_path = os.path.realpath(self.xacro_urdf_file)
        dir_path = os.path.dirname(absolute_urdf_path)
        self.get_logger().info(f'changing directory to {dir_path}')
        os.chdir(dir_path)


    def parse_file(self, target: str):
        # convert the xacro into final file
        doc = xacro.parse(open(self.xacro_urdf_file))
        xacro.process_doc(
            doc,
            mappings={'target': target} if target else None
        )
        return doc.toxml()

    def publish_file(self, contents: str, target: str):
        topic = '%s/%s' % (self.args.topic, target) if target else self.args.topic
        publisher = self.create_publisher(
            String,
            topic,
            qos_profile=self.qos)

        msg = String()
        msg.data = contents
        publisher.publish(msg)

        # publish as topic
        self.publishers.append(publisher)

        # publish as parameter
        self.declare_parameter(topic, contents)

        self.get_logger().info(f'published {target} target on {topic}')

    def parse_and_publish_file(self, target: str):
        if target == '*': target = None
        try:
            contents = self.parse_file(target)
            self.publish_file(contents, target)
        except RuntimeError as e:
            self.get_logger().error(f'cannot publish target {target} for file {self.xacro_urdf_file}')

    def run(self):
        if self.targets:
            for target in self.targets:
                self.parse_and_publish_file(target)
        else:
            self.parse_and_publish_file(None)

        rclpy.spin(self)


def main(args=sys.argv):
    rclpy.init(args=args)
    args_without_ros = rclpy.utilities.remove_ros_args(args)
    node = ResourcePublisherNode(args_without_ros)
    node.run()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
