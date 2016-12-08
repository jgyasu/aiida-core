# -*- coding: utf-8 -*-

import os

import aiida.backends.sqlalchemy
from aiida.backends.sqlalchemy.models import DbNode, DbWorkflow
from aiida.common.additions.backup_script.backup_base import AbstractBackup, BackupError
from aiida.common.folders import RepositoryFolder
from aiida.orm.node import Node
from aiida.orm.workflow import Workflow

__copyright__ = u"Copyright (c), This file is part of the AiiDA platform. For further information please visit http://www.aiida.net/. All rights reserved."
__license__ = "MIT license, see LICENSE.txt file."
__authors__ = "The AiiDA team."
__version__ = "0.7.0"


class Backup(AbstractBackup):
    """
    Backup for sqlalchemy backend
    """
    _batch_size = 50

    def _query_first_workflow(self):
        """
        Query first workflow
        :return:
        """
        res = aiida.backends.sqlalchemy.session.query(
            DbWorkflow).order_by(DbWorkflow.ctime).first()

        if res is None:
            return list()

        return [res]

    def _query_first_node(self):
        """
        Query first node
        :return:
        """
        res = aiida.backends.sqlalchemy.session.query(
            DbNode).order_by(DbNode.ctime).first()

        if res is None:
            return list()

        return [res]

    def _get_query_sets(self, start_of_backup, backup_end_for_this_round):
        """
        Get Nodes and Worflows query set from start to en

        d of backup.
        :param start_of_backup:
        :param backup_end_for_this_round:
        :return:
        """
        q_nodes = aiida.backends.sqlalchemy.session.query(
            DbNode).filter(DbNode.mtime >= start_of_backup).filter(
            DbNode.mtime <= backup_end_for_this_round)

        q_workflows = aiida.backends.sqlalchemy.session.query(
            DbWorkflow).filter(DbWorkflow.mtime >= start_of_backup).filter(
            DbWorkflow.mtime <= backup_end_for_this_round)

        return [q_nodes, q_workflows]

    def _get_query_set_iterator(self, query_set):
        """
        Get query set iterator
        :param query_set:
        :return:
        """
        return query_set.yield_per(self._batch_size)

    def _get_source_directory(self, item):
        """

        :param item:
        :return:
        """
        if type(item) == DbWorkflow:
            source_dir = os.path.normpath(RepositoryFolder(
                section=Workflow._section_name,
                uuid=item.uuid).abspath)
        elif type(item) == DbNode:
            source_dir = os.path.normpath(RepositoryFolder(
                section=Node._section_name,
                uuid=item.uuid).abspath)
        else:
            # Raise exception
            self._logger.error(
                "Unexpected item type to backup: {}"
                    .format(type(item)))
            raise BackupError(
                "Unexpected item type to backup: {}"
                    .format(type(item)))
        return source_dir
