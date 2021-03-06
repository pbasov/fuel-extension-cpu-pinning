# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from __future__ import absolute_import

from fuelclient.client import APIClient
from fuelclient.common import data_utils

from cliff import command
from cliff import lister
from cliff import show

API_URI = '/nodes/{}/cpu-pinning/'


class GetPinning(show.ShowOne, command.Command):
    columns = ('node', 'nova_cores', 'vrouter_cores')

    def take_action(self, parsed_args):
        args = parsed_args.__dict__
        data = APIClient.get_request(API_URI.format(args['node']))
        data['node'] = args['node']
        data['vrouter_cores'] = data.get('vrouter_cores', [])
        data['nova_cores'] = data.get('nova_cores', [])
        data = data_utils.get_display_data_single(self.columns, data)
        return self.columns, data

    def get_parser(self, prog_name):
        parser = super(GetPinning, self).get_parser(prog_name)
        parser.add_argument('--node', type=int, help='node id', required=True)
        return parser


class SetPinning(command.Command):
    columns = ('node', 'nova_cores', 'vrouter_cores')

    def take_action(self, parsed_args):
        args = parsed_args.__dict__
        nova_cores = [s for s in args['nova_cores'].split(',') if s]
        vrouter_cores = [s for s in args['vrouter_cores'].split(',') if s]
        data = {'nova_cores': nova_cores, 'vrouter_cores': vrouter_cores}
        result = APIClient.put_request(API_URI.format(args['node']), data)

        return self.columns, data

    def get_parser(self, prog_name):
        parser = super(SetPinning, self).get_parser(prog_name)
        parser.add_argument('--node', type=int,
                            help='node id', required=True)
        parser.add_argument('--vrouter_cores', type=str,
                            help='vrouter mask', default='')
        parser.add_argument('--nova_cores', type=str,
                            help='nova mask', default='')
        return parser


class DelPinning(command.Command):
    columns = ('node')

    def take_action(self, parsed_args):
        args = parsed_args.__dict__
        data = {'node': args['node']}
        result = APIClient.delete_request(API_URI.format(args['node']))
        return self.columns, data

    def get_parser(self, prog_name):
        parser = super(DelPinning, self).get_parser(prog_name)
        parser.add_argument('--node', type=int, help='node id', required=True)
        return parser
