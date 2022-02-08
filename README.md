# Resource Publisher

The primary purpose of this ros2 module is to publish your URDF and SRDF to a topic for use by Rviz2, gazebo,
robot dynamics and other nodes. 

## Multiple URDF Variants
In some cases you may need to publish slightly different versions of a URDF file. I found this, for example,
with Rviz2 and Gazebo requiring a few tweaks. It's easy to use xacro `if(...) then...else` to conditionally
generate the differences but both versions must still be published. If you supply the `targets` argument then
Resource Publisher will rerun xacro for each target and publish the variant with the target ID appended to
the topic name.

# Arguments
| Argument | parameter | Description |
|----------|-----------|-------------|
| --package | <PKG_NAME> | The package containing the document resource to publish
| --xacro | <FILE_NAME>  | The xacro file to substitute with parameters (found within the given package)
| --topic | <TOPIC_NAME> | topic to publish on. Target name will also be appended if set.
| --targets | <TARGETS>  | Comma-seperated list of targets. Each value will be passed to the xacro file as a "target" parameter and published on a new topic. Use * for <unset> target.

# Example Launch Description
The following example publishes two variants of the `lss_humanoid.xacro.urdf` file. The first variant has the `target` xacro parameter unset (null) and published on the topic `/robot_description`. The second variant has the `target` parameter set to 'gazebo' and is published on the topic `/robot_description/gazebo`.
```python
     urdf_publisher = Node(
        package='resource_publisher',
        executable='resource_publisher',
        output='screen',
        arguments=[
            '-package', 'lss_humanoid',
            '-xacro', 'urdf/lss_humanoid.xacro.urdf',
            '-topic', 'robot_description',
            '-targets', '*,gazebo']
    )
```
