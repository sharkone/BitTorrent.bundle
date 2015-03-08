###############################################################################
import mixpanel
import uuid

###############################################################################
TOKEN = '6e7ecd86cf4fa3cf08ddaf8ab3de81d6'

###############################################################################
def people_set(properties={}, meta={}):
    try:
        meta['$ip'] = Network.PublicAddress

        properties['Server OS']       = str(Platform.OS)
        properties['Server CPU']      = str(Platform.CPU)
        properties['Channel Version'] = SharedCodeService.common.VERSION

        mp = mixpanel.Mixpanel(TOKEN)
        mp.people_set(get_distinct_id(), properties, meta)
        Log.Info('Sent people properties')
    except Exception as exception:
        Log.Error('Unhandled exception: {0}'.format(exception))

###############################################################################
def track(event, properties={}, meta={}):
    try:
        meta['$ip'] = Network.PublicAddress

        properties['Server OS']       = str(Platform.OS)
        properties['Server CPU']      = str(Platform.CPU)
        properties['Client Product']  = str(Client.Product)
        properties['Client Platform'] = str(Client.Platform)
        properties['Channel Version'] = SharedCodeService.common.VERSION

        mp = mixpanel.Mixpanel(TOKEN)
        mp.track(get_distinct_id(), event, properties, meta)
        Log.Info('Sent tracking event: {0}'.format(event))
    except Exception as exception:
        Log.Error('Unhandled exception: {0}'.format(exception))

###############################################################################
def get_distinct_id():
    if not 'distinct_id' in Dict:
        Dict['distinct_id'] = uuid.uuid4().hex
        Dict.Save()

    return Dict['distinct_id']
