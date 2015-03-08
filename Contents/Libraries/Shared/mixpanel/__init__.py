import base64
import json
import time
import urllib
import urllib2

"""
The mixpanel package allows you to easily track events and
update people properties from your python application.

The Mixpanel class is the primary class for tracking events and
sending people analytics updates.

The Consumer and BufferedConsumer classes allow callers to
customize the IO characteristics of their tracking.
"""

VERSION = '3.1.2'


class Mixpanel(object):
    """
    Use instances of Mixpanel to track events and send Mixpanel
    profile updates from your python code.
    """

    def __init__(self, token, consumer=None):
        """
        Creates a new Mixpanel object, which can be used for all tracking.

        To use mixpanel, create a new Mixpanel object using your
        token.  Takes in a user token and an optional Consumer (or
        anything else with a send() method). If no consumer is
        provided, Mixpanel will use the default Consumer, which
        communicates one synchronous request for every message.
        """
        self._token = token
        self._consumer = consumer or Consumer()

    def _now(self):
        return time.time()

    def track(self, distinct_id, event_name, properties={}, meta={}):
        """
        Notes that an event has occurred, along with a distinct_id
        representing the source of that event (for example, a user id),
        an event name describing the event and a set of properties
        describing that event. Properties are provided as a Hash with
        string keys and strings, numbers or booleans as values.

          # Track that user "12345"'s credit card was declined
          mp.track("12345", "Credit Card Declined")

          # Properties describe the circumstances of the event,
          # or aspects of the source or user associated with the event
          mp.track("12345", "Welcome Email Sent", {
              'Email Template' => 'Pretty Pink Welcome',
              'User Sign-up Cohort' => 'July 2013'
          })
        """
        all_properties = {
            'token': self._token,
            'distinct_id': distinct_id,
            'time': int(self._now()),
            'mp_lib': 'python',
            '$lib_version': VERSION,
        }
        all_properties.update(properties)
        event = {
            'event': event_name,
            'properties': all_properties,
        }
        event.update(meta)
        self._consumer.send('events', json.dumps(event, separators=(',', ':')))

    def alias(self, alias_id, original, meta={}):
        """
        Gives custom alias to a people record.

        Alias sends an update to our servers linking an existing distinct_id
        with a new id, so that events and profile updates associated with the
        new id will be associated with the existing user's profile and behavior.
        Example:
            mp.alias('amy@mixpanel.com', '13793')
        """
        self.track(original, '$create_alias', {
            'distinct_id': original,
            'alias': alias_id,
            'token': self._token,
        }, meta=meta)

    def people_set(self, distinct_id, properties, meta={}):
        """
        Set properties of a people record.

        Sets properties of a people record given in JSON object. If the profile
        does not exist, creates new profile with these properties.
        Example:
            mp.people_set('12345', {'Address': '1313 Mockingbird Lane',
                                    'Birthday': '1948-01-01'})
        """
        return self.people_update({
            '$distinct_id': distinct_id,
            '$set': properties,
        }, meta=meta)

    def people_set_once(self, distinct_id, properties, meta={}):
        """
        Set immutable properties of a people record.

        Sets properties of a people record given in JSON object. If the profile
        does not exist, creates new profile with these properties. Does not
        overwrite existing property values.
        Example:
            mp.people_set_once('12345', {'First Login': "2013-04-01T13:20:00"})
        """
        return self.people_update({
            '$distinct_id': distinct_id,
            '$set_once': properties,
        }, meta=meta)

    def people_increment(self, distinct_id, properties, meta={}):
        """
        Increments/decrements numerical properties of people record.

        Takes in JSON object with keys and numerical values. Adds numerical
        values to current property of profile. If property doesn't exist adds
        value to zero. Takes in negative values for subtraction.
        Example:
            mp.people_increment('12345', {'Coins Gathered': 12})
        """
        return self.people_update({
            '$distinct_id': distinct_id,
            '$add': properties,
        }, meta=meta)

    def people_append(self, distinct_id, properties, meta={}):
        """
        Appends to the list associated with a property.

        Takes a JSON object containing keys and values, and appends each to a
        list associated with the corresponding property name. $appending to a
        property that doesn't exist will result in assigning a list with one
        element to that property.
        Example:
            mp.people_append('12345', { "Power Ups": "Bubble Lead" })
        """
        return self.people_update({
            '$distinct_id': distinct_id,
            '$append': properties,
        }, meta=meta)

    def people_union(self, distinct_id, properties, meta={}):
        """
        Merges the values for a list associated with a property.

        Takes a JSON object containing keys and list values. The list values in
        the request are merged with the existing list on the user profile,
        ignoring duplicate list values.
        Example:
            mp.people_union('12345', { "Items purchased": ["socks", "shirts"] } )
        """
        return self.people_update({
            '$distinct_id': distinct_id,
            '$union': properties,
        }, meta=meta)

    def people_unset(self, distinct_id, properties, meta={}):
        """
        Removes properties from a profile.

        Takes a JSON list of string property names, and permanently removes the
        properties and their values from a profile.
        Example:
            mp.people_unset('12345', ["Days Overdue"])
        """
        return self.people_update({
            '$distinct_id': distinct_id,
            '$unset': properties,
        }, meta=meta)

    def people_delete(self, distinct_id, meta={}):
        """
        Permanently deletes a profile.

        Permanently delete the profile from Mixpanel, along with all of its
        properties.
        Example:
            mp.people_delete('12345')
        """
        return self.people_update({
            '$distinct_id': distinct_id,
            '$delete': "",
        }, meta=meta)

    def people_track_charge(self, distinct_id, amount, properties={}, meta={}):
        """
        Tracks a charge to a user.

        Record that you have charged the current user a certain amount of
        money. Charges recorded with track_charge will appear in the Mixpanel
        revenue report.
        Example:
            #tracks a charge of $50 to user '1234'
            mp.people_track_charge('1234', 50)

            #tracks a charge of $50 to user '1234' at a specific time
            mp.people_track_charge('1234', 50, {'$time': "2013-04-01T09:02:00"})
        """
        properties.update({'$amount': amount})
        return self.people_append(distinct_id, {'$transactions': properties}, meta=meta)

    def people_clear_charges(self, distinct_id, meta={}):
        """
        Clears all charges from a user.

        Clears all charges associated with a user profile on Mixpanel.
        Example:
            #clear all charges from user '1234'
            mp.people_clear_charges('1234')
        """
        return self.people_unset(distinct_id, ["$transactions"], meta=meta)

    def people_update(self, message, meta={}):
        """
        Send a generic update to Mixpanel people analytics.

        Caller is responsible for formatting the update message, as
        documented in the Mixpanel HTTP specification, and passing
        the message as a dict to update. This
        method might be useful if you want to use very new
        or experimental features of people analytics from python
        The Mixpanel HTTP tracking API is documented at
        https://mixpanel.com/help/reference/http
        """
        record = {
            '$token': self._token,
            '$time': int(self._now() * 1000),
        }
        record.update(message)
        record.update(meta)
        self._consumer.send('people', json.dumps(record, separators=(',', ':')))


class MixpanelException(Exception):
    """
    MixpanelExceptions will be thrown if the server can't recieve
    our events or updates for some reason- for example, if we can't
    connect to the Internet.
    """
    pass


class Consumer(object):
    """
    The simple consumer sends an HTTP request directly to the Mixpanel service,
    with one request for every call. This is the default consumer for Mixpanel
    objects- if you don't provide your own, you get one of these.
    """
    def __init__(self, events_url=None, people_url=None):
        self._endpoints = {
            'events': events_url or 'https://api.mixpanel.com/track',
            'people': people_url or 'https://api.mixpanel.com/engage',
        }

    def send(self, endpoint, json_message):
        """
        Record an event or a profile update. Send is the only method
        associated with consumers. Will raise an exception if the endpoint
        doesn't exist, if the server is unreachable or for some reason
        can't process the message.

        All you need to do to write your own consumer is to implement
        a send method of your own.

        :param endpoint: One of 'events' or 'people', the Mixpanel endpoint for sending the data
        :type endpoint: str (one of 'events' or 'people')
        :param json_message: A json message formatted for the endpoint.
        :type json_message: str
        :raises: MixpanelException
        """
        if endpoint in self._endpoints:
            self._write_request(self._endpoints[endpoint], json_message)
        else:
            raise MixpanelException('No such endpoint "{0}". Valid endpoints are one of {1}'.format(self._endpoints.keys()))

    def _write_request(self, request_url, json_message):
        data = urllib.urlencode({
            'data': base64.b64encode(json_message),
            'verbose': 1,
            'ip': 0,
        })
        try:
            request = urllib2.Request(request_url, data)
            response = urllib2.urlopen(request).read()
        except urllib2.HTTPError as e:
            raise MixpanelException(e)

        try:
            response = json.loads(response)
        except ValueError:
            raise MixpanelException('Cannot interpret Mixpanel server response: {0}'.format(response))

        if response['status'] != 1:
            raise MixpanelException('Mixpanel error: {0}'.format(response['error']))

        return True


class BufferedConsumer(object):
    """
    BufferedConsumer works just like Consumer, but holds messages in
    memory and sends them in batches. This can save bandwidth and
    reduce the total amount of time required to post your events.

    Because BufferedConsumers hold events, you need to call flush()
    when you're sure you're done sending them. calls to flush() will
    send all remaining unsent events being held by the BufferedConsumer.
    """
    def __init__(self, max_size=50, events_url=None, people_url=None):
        self._consumer = Consumer(events_url, people_url)
        self._buffers = {
            'events': [],
            'people': [],
        }
        self._max_size = min(50, max_size)

    def send(self, endpoint, json_message):
        """
        Record an event or a profile update. Calls to send() will store
        the given message in memory, and (when enough messages have been stored)
        may trigger a request to Mixpanel's servers.

        Calls to send() may throw an exception, but the exception may be
        associated with the message given in an earlier call. If this is the case,
        the resulting MixpanelException e will have members e.message and e.endpoint

        :param endpoint: One of 'events' or 'people', the Mixpanel endpoint for sending the data
        :type endpoint: str (one of 'events' or 'people')
        :param json_message: A json message formatted for the endpoint.
        :type json_message: str
        :raises: MixpanelException
        """
        if endpoint not in self._buffers:
            raise MixpanelException('No such endpoint "{0}". Valid endpoints are one of {1}'.format(self._buffers.keys()))

        buf = self._buffers[endpoint]
        buf.append(json_message)
        if len(buf) >= self._max_size:
            self._flush_endpoint(endpoint)

    def flush(self):
        """
        Send all remaining messages to Mixpanel.

        BufferedConsumers will flush automatically when you call send(), but
        you will need to call flush() when you are completely done using the
        consumer (for example, when your application exits) to ensure there are
        no messages remaining in memory.

        Calls to flush() may raise a MixpanelException if there is a problem
        communicating with the Mixpanel servers. In this case, the exception
        thrown will have a message property, containing the text of the message,
        and an endpoint property containing the endpoint that failed.

        :raises: MixpanelException
        """
        for endpoint in self._buffers.keys():
            self._flush_endpoint(endpoint)

    def _flush_endpoint(self, endpoint):
        buf = self._buffers[endpoint]
        while buf:
            batch = buf[:self._max_size]
            batch_json = '[{0}]'.format(','.join(batch))
            try:
                self._consumer.send(endpoint, batch_json)
            except MixpanelException as e:
                e.message = 'batch_json'
                e.endpoint = endpoint
            buf = buf[self._max_size:]
        self._buffers[endpoint] = buf
