import os
import logging

from nailgun import objects
from nailgun.logger import logger

from nailgun.extensions import BaseExtension
from nailgun.extensions import BasePipeline

from fuel_extension_cpu_pinning.models import CpuPinOverride
from fuel_extension_cpu_pinning import handlers


class PinningOverridePipeline(BasePipeline):
    @classmethod
    def _generate_kernel_params(cls, kparams, pins_data):
        pins_str = ','.join(pins_data.nova_cores + pins_data.vrouter_cores)
        isolcpus = 'isolcpus={}'.format(pins_str)
        for param in kparams:
            if 'isolcpus' in param:
                kparams[kparams.index(param)] = isolcpus
            if isolcpus not in kparams:
                kparams.append(isolcpus)
        logger.debug('Generating kernel parameters data')
        return ' '.join(kparams)

    @classmethod
    def process_provisioning(cls, data, cluster, nodes, **kwargs):
        """Find and replace isolcpus kernel parameter in provisioning data
           Find compute nodes in the data, lookup kernel parameters,
           update or append parameters with values from the pins table.
        """
        nodes_data = [node for node in data['nodes']]

        for node_data in nodes_data:
            pins_data = CpuPinOverride.get_by_uid(node_data['uid'])
            if pins_data:
                kparams = node_data['ks_meta']['pm_data']['kernel_params']
                newkparams = PinningOverridePipeline._generate_kernel_params(
                             kparams.split(), pins_data)
                node_data['ks_meta']['pm_data']['kernel_params'] = newkparams

        logger.debug('Overriding isolcpu values in grub')
        logger.debug(data)
        return data

    @classmethod
    def process_deployment(cls, data, cluster, nodes, **kwargs):
        nodes_data = [node_data for node_data in data
                      if node_data['uid'] != 'master']
        pinning_nodes = [node_data['uid'] for node_data in nodes_data
                         if CpuPinOverride.get_by_uid(node_data['uid'])]
        logger.debug(pinning_nodes)

        for node_data in nodes_data:
            pins_data = CpuPinOverride.get_by_uid(node_data['uid'])
            if pins_data:
                pinning_nodes.append(node_data['uid'])
                node_data['nova']['cpu_pinning'] = pins_data.nova_cores
                kparams = node_data['kernel_params']['kernel']
                newkparams = PinningOverridePipeline._generate_kernel_params(
                             kparams.split(), pins_data)
                node_data['kernel_params']['kernel'] = newkparams
                node_data['release']['attributes_metadata']['editable'][
                          'kernel_params']['kernel']['value'] = newkparams

            if pins_data.vrouter_cores and 'dpdk' in node_data['roles']:
                pins_str = ','.join(pins_data.nova_cores + pins_data.vrouter_cores)
                node_data['contrail']['vrouter_core_mask'] = pins_str

            for nm_key, nm_val in node_data['network_metadata']['nodes'].items():
                if nm_val['uid'] in pinning_nodes:
                    nm_val['nova_cpu_pinning_enabled'] = True
        logger.debug('Overriding CPU pinning values in deployment data')
        return data


class CpuPinningExtension(BaseExtension):
    name = 'cpu_pinning_override'
    version = '1.0.0'
    description = 'CPU pinning override for Nova and vrouter'

    urls = [{'uri': r'/nodes/(?P<node_id>\d+)/cpu-pinning/?$',
             'handler': handlers.CpuPinningHandler}]

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
