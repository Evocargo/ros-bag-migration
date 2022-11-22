# ros-bag-migration

ros-bag-migration tool allows you to change the format of messages in recorded bags in
ROS 1. This may be needed when you decide to record new bags with an updated set of
message definitions, and you want to change older bags accordingly for compatibility.

Apart from the basic migration operations that are also present in the
[standard ros-tool](http://wiki.ros.org/rosbag/migration), ros-bag-migration offers
additional features:

<img src="./images/Frame 4.png"/>

## System requirements

- ROS 1 tested with melodic, may be compatible with other ROS 1 distributions
- Cpack
- Python 3.6
- Ubuntu 18

## How it works

ros-bag-migration tool allows you to create a stack of rules that will be applied
sequentially to a bag, a list or a folder of bags that you define as input. The tool scans
messages in this bag for specified parameters, e.g. a certain topic name, to detect
messages that should be changed, and then applies your rules to them. After completing,
the tool returns a backup of the old bag in a _.bak file stored in the specified location
and a new _.bag file.

<img src="./images/Frame 1.png"/>

You can use this tool with a bunch of bags at a time, just keep in mind that the number of
your bags will double after migration.

## Versioning

Let's consider versioning based on the example. Let’s say we have bags recorded on an
autonomous car.

One of the messages in these bags includes the task, e.g. ‘turn right’ or ‘move forward’,
and the corresponding signals, e.g. use of the turn signal, steering direction, how fast
the car turns the steering wheel. That’s a lot for one message, so we split it in two –
the one for the task and the other one for signals – and specify the topics for new
messages. This is our migration rule 1.

Next, we find a misprint in one of the topic names and want to correct the name in all the
recorded bags. This is rule 2.

<img src="./images/Frame 2.png"/>

When we run the tool on selected bags, the rules are applied one by one, and we get bags
of version 2. Later on, we decide to add the rear steer field to the ‘signals’ message, so
we extend our stack of rules.

<img src="./images/Frame 3.png"/>

When we run the tool on the bags we’ve migrated before, their version is defined (ver. 2)
and only one new rule is applied to update them to version 3. The bags we’ve never
migrated before are updated from version 0 to version 3.

## Rules overview

Rules are defined in a \*.py file by using the following classes:

```python
class Migrate(Base):
   """Migrate rule for update bag information"""

   @staticmethod
   def version() -> int:
   """Return the current version of migrate. The version number must be unique"""
       ...


   def migrate(self, in_msg: Any, src_topic: str) -> Dict[str, Any]:
   """Update the message or topic if needed or return the source data in dict : {src_topic: in_msg}"""
       ...
```

Please see the example [here](./src/bag_migration/examples_rule.py). 

## Build package

```bash
mkdir build
cd build

# set parametrs to build package for python 3
export PYTHONDONTWRITEBYTECODE=1
export ROS_PYTHON_VERSION=3

# create package
cmake -DCMAKE_BUILD_TYPE=Release -DCATKIN_ENABLE_TESTING=OFF -DCATKIN_BUILD_BINARY_PACKAGE=ON ..
cpack -D CPACK_CMAKE_GENERATOR=Ninja
```

## To work without install

After make package use this command:

```bash
source build/devel/setup.bash --extend
```

## Install package

```bash
sudo apt install ./ros-melodic-bag-migration_1.0.0_amd64.deb
```

## Example

To test this tool, use `test.bag` from the `data` folder and the example rules:

```bash
mkdir output
mkdir backup
mkdir tmp

rosrun bag_migration migrate_bag.py ./data --output ./output --output-backup ./backup --bag-version 0 --migrate-version 3 --tmp-dir ./tmp
```

## Ideas for further development

This bag migration tool can be reconfigured to migrate ROS2 bags to a new format or even
to migrate data from ROS1 to ROS2 bags.
