from __future__ import unicode_literals, division, absolute_import
from future.moves.urllib.parse import quote, urlparse, parse_qs
from builtins import *  # noqa pylint: disable=unused-import, redefined-builtin

import logging
import re

from flexget import plugin
from flexget.entry import Entry
from flexget.event import event
from flexget.utils.requests import RequestException
from flexget.utils.soup import get_soup
from flexget.components.sites.utils import torrent_availability
from flexget.utils.tools import parse_filesize
from flexget.components.sites.urlrewriting import UrlRewritingError

log = logging.getLogger('rutracker')


class SiteRutracker(object):
    schema = {'type': 'boolean'}

    base_url = 'https://api.t-ru.org'

    # urlrewriter API
    def url_rewritable(self, task, entry):
        url = entry['url']
        if url.startswith('https://rutracker.org/forum/viewtopic.php?t='):
            return True
        return False

    @plugin.internet(log)
    def url_rewrite(self, task, entry):
        """
            Gets torrent information for topic from rutracker api
        """

        url = entry['url']
        log.info('rewriting download url: %s' % url)

        topic_id = parse_qs(urlparse(url).query)['t'][0]

        api_url = self.base_url + '/v1/get_tor_topic_data?by=topic_id&val=%s' % topic_id
        log.debug('requesting: %s', api_url)
        topic_request = task.requests.get(api_url)

        topic = topic_request.json()['result'][topic_id]

        magnet_url = 'magnet:?xt=urn:btih:' +  topic['info_hash']  + '&tr=http%3A%2F%2Fbt.t-ru.org%2Fann%3Fmagnet'
        entry['url'] = magnet_url

@event('plugin.register')
def register_plugin():
    plugin.register(SiteRutracker, 'rutracker', interfaces=['urlrewriter'], api_ver=2)
