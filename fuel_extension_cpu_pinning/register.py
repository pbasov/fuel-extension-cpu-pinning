from nailgun.db import db
from nailgun.db.sqlalchemy.models import Cluster
from nailgun.db.sqlalchemy.models import Release


def set_extensions(nailgun_objects):
    for obj, extensions in nailgun_objects.items():
        extensions.append(u'cpu_pinning_override')
        extensions = list(set(extensions))
        obj.extensions = extensions
        db().flush()

clusters = {cl: cl['extensions'] for cl in db().query(Cluster).all()}
releases = {rl: rl['extensions'] for rl in db().query(Release).all()}

set_extensions(clusters)
set_extensions(releases)

db().flush()
db().commit()
