#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : runner.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: 
"""

# system modules
import argparse
import logging
import yaml

# local modules
from CHAP.pipeline import Pipeline


class OptionParser():
    """User based option parser"""
    def __init__(self):
        """OptionParser class constructor"""
        self.parser = argparse.ArgumentParser(prog='PROG')
        self.parser.add_argument(
            '--config', action='store', dest='config',
            default='', help='Input configuration file')
        self.parser.add_argument(
            '--interactive', action='store_true', dest='interactive',
            help='Allow interactive processes')
        self.parser.add_argument(
            '--log-level', choices=logging._nameToLevel.keys(),
            dest='log_level', default='INFO', help='logging level')


def main():
    """Main function"""
    optmgr  = OptionParser()
    opts = optmgr.parser.parse_args()
    runner(opts)


def runner(opts):
    """Main runner function

    :param opts: object containing input parameters
    :type opts: OptionParser
    """

    logger = logging.getLogger(__name__)
    log_level = getattr(logging, opts.log_level.upper())
    logger.setLevel(log_level)
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(logging.Formatter(
        '{name:20}: {message}', style='{'))
    logger.addHandler(log_handler)

    config = {}
    with open(opts.config) as file:
        config = yaml.safe_load(file)
    logger.info(f'Input configuration: {config}\n')
    pipeline_config = config.get('pipeline', [])
    objects = []
    kwds = []
    for item in pipeline_config:
        # load individual object with given name from its module
        kwargs = {'interactive': opts.interactive}
        if isinstance(item, dict):
            name = list(item.keys())[0]
            # Combine the "interactive" command line argument with the
            # object's keywords giving precedence of "interactive" in
            # the latter
            kwargs = {**kwargs, **item[name]}
        else:
            name = item
            kwargs = {}
        mod_name, cls_name = name.split('.')
        module = __import__(f'CHAP.{mod_name}', fromlist=[cls_name])
        obj = getattr(module, cls_name)()
        obj.logger.setLevel(log_level)
        obj.logger.addHandler(log_handler)
        logger.info(f'Loaded {obj}')
        objects.append(obj)
        kwds.append(kwargs)
    pipeline = Pipeline(objects, kwds)
    pipeline.logger.setLevel(log_level)
    pipeline.logger.addHandler(log_handler)
    logger.info(f'Loaded {pipeline} with {len(objects)} items\n')
    logger.info(f'Calling "execute" on {pipeline}')
    pipeline.execute()


if __name__ == '__main__':
    main()
