from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.dialects import postgresql as psql

from nailgun.db import db
from nailgun.errors import errors
from nailgun.db.sqlalchemy.models.base import Base


class CpuPinOverride(Base):
    __tablename__ = 'cpu_pinning_override_pins'
    id = Column(Integer, primary_key=True)
    nova_cores = Column(psql.ARRAY(String(255)),
                        default=[], nullable=False, server_default='{}')
    vrouter_cores = Column(psql.ARRAY(String(255)),
                           default=[], nullable=False, server_default='{}')

    @classmethod
    def get_by_uid(cls, uid, fail_if_not_found=False, lock_for_update=False):
        """Get instance by it's uid (PK in case of SQLAlchemy)

        :param uid: uid of object
        :param fail_if_not_found: raise an exception if object is not found
        :param lock_for_update: lock returned object for update (DB mutex)
        :returns: instance of an object (model)
        """
        q = db().query(CpuPinOverride)
        if lock_for_update:
            q = q.with_lockmode('update')
        res = q.get(uid)
        if not res and fail_if_not_found:
            raise errors.ObjectNotFound(
                "Object '{0}' with UID={1} is not found in DB".format(
                    cls.__name__,
                    uid
                )
            )
        return res

    @classmethod
    def update(cls, instance):
        """Update existing instance with specified parameters

        :param instance: object (model) instance
        :param data: dictionary of key-value pairs as object fields
        :returns: instance of an object (model)
        """
        db().add(instance)
        db().flush()
        db().commit()
        return instance

    @classmethod
    def delete(cls, instance):
        db().delete(instance)
        db().flush()
        db().commit()
        return instance
