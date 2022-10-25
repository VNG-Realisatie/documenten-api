from django.conf import settings

from notifications_api_common.kanalen import Kanaal

from drc.datamodel.models import EnkelvoudigInformatieObject

KANAAL_DOCUMENTEN = Kanaal(
    settings.NOTIFICATIONS_KANAAL,
    main_resource=EnkelvoudigInformatieObject,
    kenmerken=(
        "bronorganisatie",
        "informatieobjecttype",
        "vertrouwelijkheidaanduiding",
    ),
)
