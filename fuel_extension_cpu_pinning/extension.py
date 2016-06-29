import os
import logging

from nailgun.extensions import BaseExtension
from nailgun.extensions import BasePipeline

logger = logging.getLogger(__name__)


class PinningOverridePipeline(BasePipeline):

    @classmethod
    def process_provisioning(cls, data, cluster, nodes, **kwargs):
        # Fix pinning values in grub
        return data

    @classmethod
    def process_deployment(cls, data, cluster, nodes, **kwargs):
        # Fix pinning values in astute.yaml
        return data


class CpuPinningExtension(BaseExtension):
    name = 'cpu_pinning_override'
    version = '1.0.0'
    description = 'CPU pinning override for Nova and vrouter'

    data_pipelines = [
        PinningOverridePipeline,
    ]

    @classmethod
    def alembic_migrations_path(cls):
        return os.path.join(os.path.dirname(__file__), 'migrations')

    @classmethod
    def on_node_delete(cls, node):
        logging.debug('Node %s has been deleted', node.id)

    @classmethod
    def on_cluster_delete(cls, cluster):
        logging.debug('Cluster %s has been deleted', cluster.id)
