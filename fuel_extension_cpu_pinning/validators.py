from fuel_extension_cpu_pinning.models import CpuPinOverride
from nailgun.api.v1.validators.base import BasicValidator
from nailgun.errors import errors
from nailgun.logger import logger


class CpuPinningValidator(BasicValidator):
    schema = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "title": "CPU pinning for Nova and Contrail vrouter",
        "description": "CPU cores masks",
        "type": "object",
        "properties": {
            "nova_cores": {"type": "array"},
            "vrouter_cores": {"type": "array"},
        },
    }

    @classmethod
    def validate(cls, data, node=None, pins_data=None):
        """Check input data for intersections
           to ensure correct core bindings
        """
        dict_data = cls.validate_json(data)
        cls.validate_schema(dict_data, cls.schema)

        api_nova_cores = dict_data.get('nova_cores', [])
        api_vrouter_cores = dict_data.get('vrouter_cores', [])
        db_nova_cores = pins_data.get('nova_cores') or []
        db_vrouter_cores = pins_data.get('vrouter_cores') or []

        if set(api_nova_cores) & set(api_vrouter_cores) != set():
            raise errors.InvalidData('Input values conflict with each other')

        if all(cores != [] for cores in (api_nova_cores, api_vrouter_cores)):
            return dict_data

        if any(condition != set() for condition in [
            set(api_nova_cores) & set(db_vrouter_cores),
            set(api_vrouter_cores) & set(db_nova_cores)]
        ):
            raise errors.InvalidData('Input values conflict with existing one')
        return dict_data
