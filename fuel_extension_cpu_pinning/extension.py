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
                break
        else:
            kparams.append(isolcpus)
        logger.debug('Generating kernel parameters data')
        return ' '.join(kparams)

    @classmethod
    def process_provisioning(cls, data, cluster, nodes, **kwargs):
        """Find and replace isolcpus kernel parameter in provisioning data
           Lookup kernel parameters, update or append parameters with values
           from the pins table.
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
        """Find and replace cpu pinning parameters in deployment data,
           this includes changing nova hash, nodes hash on every node and
           contrail plugin parameters.
        """
        nodes_data = [node_data for node_data in data
                      if node_data['uid'] != 'master']
        pinning_nodes = [node_data['uid'] for node_data in nodes_data
                         if CpuPinOverride.get_by_uid(node_data['uid'])]
        logger.debug(pinning_nodes)

        for node_data in nodes_data:
            pins_data = CpuPinOverride.get_by_uid(node_data['uid'])
            if pins_data:
                # Setting nova cores and kernel params
                node_data['nova']['cpu_pinning'] = pins_data.nova_cores
                kparams = node_data['kernel_params']['kernel']
                newkparams = PinningOverridePipeline._generate_kernel_params(
                             kparams.split(), pins_data)
                node_data['kernel_params']['kernel'] = newkparams
                node_data['release']['attributes_metadata']['editable'][
                          'kernel_params']['kernel']['value'] = newkparams

                # Setting contrail vrouter coremask
                if pins_data.vrouter_cores and 'dpdk' in node_data['roles']:
                    pins_str = ','.join(pins_data.vrouter_cores)
                    # vn637v. Concatenate pins + empty string to convert value from
                    # FixNum to String
                    node_data['contrail']['vrouter_core_mask'] = ' ' + pins_str

            # Overriding network_metadata['nodes'] hash on all nodes
            for nm_val in node_data['network_metadata']['nodes'].values():
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
        pins_data = CpuPinOverride.get_by_uid(node.id)
        if pins_data:
            CpuPinOverride.delete(pins_data)
            logging.debug('CPU pinning data for node {}'
                          ' has been deleted'.format(node.id))
