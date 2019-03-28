from django.conf import settings

from vng_api_common.notifications.kanalen import Kanaal

from drc.datamodel.models import EnkelvoudigInformatieObject

KANAAL_DOCUMENTEN = Kanaal(
    settings.NOTIFICATIONS_KANAAL,
    main_resource=EnkelvoudigInformatieObject,
    kenmerken=(
        'bronorganisatie',
        'informatieobjecttype',
        'vertrouwelijkheidaanduiding'
    )
)
