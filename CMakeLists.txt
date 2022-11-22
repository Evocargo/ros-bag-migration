cmake_minimum_required(VERSION 3.10.0)
project(bag_migration VERSION 1.0.0)
set(CMAKE_INSTALL_PREFIX "/opt/ros/melodic")

find_package(catkin REQUIRED COMPONENTS
  rospy
)

catkin_python_setup()

catkin_package()

catkin_install_python(
  PROGRAMS
    scripts/migrate_bag.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

####################################################################
##                     CPACK CONFIGURATION                        ##
####################################################################
set(CPACK_GENERATOR "DEB")
set(CPACK_PACKAGING_INSTALL_PREFIX "/opt/ros/melodic")

string(REGEX REPLACE "_" "-" DASH_PROJECT_NAME ${PROJECT_NAME})

set(CPACK_PACKAGE_VERSION ${PROJECT_VERSION})
set(CPACK_PACKAGE_NAME "ros-melodic-${DASH_PROJECT_NAME}")
set(CPACK_DEBIAN_PACKAGE_MAINTAINER "Burmistrov Vladimir <vladimir.burmistrov@evocargo.com>")
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "ROS package interactions with the bag migration util.")
set(CPACK_DEBIAN_FILE_NAME DEB-DEFAULT)
set(CPACK_RESOURCE_FILE_README ${CMAKE_CURRENT_SOURCE_DIR}/README.md)
set(CPACK_RESOURCE_FILE_LICENSE ${CMAKE_CURRENT_SOURCE_DIR}/LICENSE.md)
set(CPACK_DEBIAN_PACKAGE_DEPENDS "python3-tqdm,
    ros-melodic-geometry-msgs"
)
include(CPack)
