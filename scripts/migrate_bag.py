#!/usr/bin/env python3
import argparse
import logging
import shutil
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List

import rospy
from rosbag import Bag
from tqdm import tqdm

from bag_migration import BaseRule, get_rules

FORMAT_BAG_VERSION = "_v{bag_version}.bag"
FORMAT_BAG_NAME = "{old_name_stem}_v{migrate_version}.bag"


def parse_args():
    """Parse params"""
    parser = argparse.ArgumentParser(
        description="Bags path to migrate topic name or msgs."
    )
    parser.add_argument("source", nargs="+", help="list of bag dirs")
    parser.add_argument("--output", required=True, help="path to save migrate bags")
    parser.add_argument(
        "--output-backup", required=True, help="path to save backup migrate bags"
    )
    parser.add_argument(
        "--bag-version",
        required=True,
        type=int,
        help="migrate bag version, example: 1 or 2",
    )
    parser.add_argument(
        "--migrate-version",
        required=True,
        type=int,
        help="Version to migrate bag, example: 2 or 3",
    )
    parser.add_argument(
        "--tmp-dir",
        required=True,
        help="Dir where bags will be located until they are migrated",
    )
    args = parser.parse_args()
    return args


def bags_to_migrate(source_args: List[str]) -> List[Path]:
    """Search for all files by the path or directory specified by the user
    Args:
        source_args: list of path to bag or path to directory where find bag
    Return:
        list of bag names with full path
    """
    bag_source = []

    for source in source_args:
        source = Path(source)
        for bag_fname in source.iterdir():
            if bag_fname.suffix == ".bag":
                bag_source.append(bag_fname)
            else:
                logging.error(f"Undefined name bag name : {bag_fname}")

    return bag_source


def configure_migrate_name(bag_fname: Path, bag_version: int, migrate_version: int):
    """Configure bag name for migration bag name"""
    if bag_fname.stem.endswith(FORMAT_BAG_VERSION.format(bag_version=bag_version)):
        migrate_bag_name = bag_fname.name.replace(
            f"v{bag_version}", f"v{migrate_version}"
        )
    else:
        migrate_bag_name = FORMAT_BAG_NAME.format(
            old_name_stem=bag_fname.stem, migrate_version=migrate_version
        )

    return migrate_bag_name


def merge_process_data(
    topic_dicts: Dict[str, Any], process_data: Dict[str, Any], source_topic: str
) -> Dict[str, Any]:
    """Merge 2 dicts to one with some rules

    Get from topic_dicts all topics and check that they topics exist in process_data
    if topics doesnt exist in topic process_data source_topic dont append to return dict

    Arguments:
        topic_dicts: source dict with data {topic: msg}
        process_data: data after rules iwht type {topic: msg}
        source_topic: topic of message that can be before rule

    >>> topic_dicts = {'topic_1': '1', 'topic_2': '2'}
    >>> process_data = {'topic_3': '1_3', 'topic_4': '1_4'}
    >>> source_topic = 'topic_1'
    >>> merge_process_data(topic_dicts, process_data, source_topic)
    {'topic_3': '1_3', 'topic_4': '1_4', 'topic_2': '2'}
    >>> process_data['topic_1'] = '1_1'
    >>> merge_process_data(topic_dicts, process_data, source_topic)
    {'topic_3': '1_3', 'topic_4': '1_4', 'topic_2': '2', 'topic_1': '1_1'}
    """

    merge_data = deepcopy(process_data)

    for topic, msg in topic_dicts.items():
        if topic != source_topic:
            merge_data[topic] = msg

    return merge_data


def update_message(
    topic_name: str,
    msg: Any,
    time: rospy.Time,
    rules_list: List[BaseRule],
    migrate_bag: Bag,
):
    """Update message and write to new bag

    Args:
        topic_name: name of topic from bag
        msg: msg from bag
        time: message time from bag
        rules_list: list of rules to migrate message
        migrate_bag: bag object to write updated message
    """
    topic_dicts = {topic_name: msg}
    for rule in rules_list:
        for topic_p, msg_p in topic_dicts.items():
            process_data = rule.migrate(topic_p, msg_p)
            topic_dicts = merge_process_data(topic_dicts, process_data, topic_p)

    for topic_m, msg_m in topic_dicts.items():
        migrate_bag.write(topic_m, msg_m, time)


def main():
    """Bag migration
    Examples:
        The migrate bag with name 'ckad_n1-003_2021-08-05-11-05-16Z.evo1b_record_default'
        result is saved as:
            migrate_bag: output / ckad / n1-003 / migrate / <bag_name>.bag
            source_bag: output_backup / <bag_name>.bag.bak
    """
    args = parse_args()

    output_backup = Path(args.output_backup)
    output_backup.mkdir(exist_ok=True, parents=True)

    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True, parents=True)

    bag_source = bags_to_migrate(args.source)
    for source in tqdm(bag_source, desc="Proceesing of bag"):
        rules_list = get_rules(args.bag_version, args.migrate_version)
        if len(rules_list) < 1:
            logging.warning(f"Bag {source} dont need migration")
            continue

        migrate_bag_name = configure_migrate_name(
            source, args.bag_version, args.migrate_version
        )

        output_path_migrate_bag = output_dir / migrate_bag_name

        tmp_migrate_bag = Path(args.tmp_dir) / migrate_bag_name
        migrate_bag = Bag(tmp_migrate_bag, "w")

        with Bag(source) as bag:
            for (
                topic_name,
                msg,
                time,
            ) in bag.read_messages():
                update_message(topic_name, msg, time, rules_list, migrate_bag)

        migrate_bag.close()

        shutil.move(tmp_migrate_bag, output_path_migrate_bag)

        shutil.move(source, output_backup / f"{source.name}.bak")


if __name__ == "__main__":
    main()
