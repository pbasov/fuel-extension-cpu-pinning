import json
import web

from nailgun.api.v1.handlers.base import BaseHandler
from nailgun.api.v1.handlers.base import content
from nailgun import objects
from nailgun.logger import logger

from fuel_extension_cpu_pinning import validators
from fuel_extension_cpu_pinning.models import CpuPinOverride


class CpuPinningHandler(BaseHandler):
    @content
    def GET(self, node_id):
        pins_data = CpuPinOverride.get_by_uid(node_id)
        if pins_data:
            return json.dumps(dict(pins_data))
        else:
            return json.dumps({})

    @content
    def PUT(self, node_id):
        pins_data = CpuPinOverride.get_by_uid(node_id)
        if not pins_data:
            pins_data = CpuPinOverride()
            pins_data.id = node_id
        validator = validators.CpuPinningValidator
        api_data = self.checked_data(validator.validate,
                                     data=web.data(),
                                     pins_data=pins_data)
        api_nova_cores = api_data.get('nova_cores')
        api_vrouter_cores = api_data.get('vrouter_cores')
        db_nova_cores = pins_data.get('nova_cores', [])
        db_vrouter_cores = pins_data.get('vrouter_cores', [])

        if not api_nova_cores:
            api_nova_cores = db_nova_cores
        if not api_vrouter_cores:
            api_vrouter_cores = db_vrouter_cores

        pins_data.vrouter_cores = api_vrouter_cores
        pins_data.nova_cores = api_nova_cores
        CpuPinOverride.update(pins_data)
        return json.dumps(dict(pins_data))

    @content
    def DELETE(self, node_id):
        pins_data = CpuPinOverride.get_by_uid(node_id)
        if pins_data:
            CpuPinOverride.delete(pins_data)
            return json.dumps(dict(pins_data))
        else:
            json.dumps({})
