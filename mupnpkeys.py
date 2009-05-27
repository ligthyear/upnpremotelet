# -*- coding: utf-8 -*-

# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php

# Copyright 2009 - Benjamin Kampmann <ben.kampmann@googlemail.com>

import os

if __name__ == '__main__':
    from twisted.internet import gtk2reactor
    gtk2reactor.install()
from coherence import log
from coherence.upnp.core.utils import parse_xml, getPage, means_true


class MediaRendererClient(log.Loggable):

    def __init__(self, coherence):
        self.coherence = coherence
        self.volume = None
        self.muted = False
        self.device = None

    def connect(self, device):
        assert self.device is None, """Don't connect as long as another device is still connected, stupid"""
        self.device = device
        service = self.device.get_service_by_type('RenderingControl')
        service.subscribe_for_variable('Volume',
                callback=lambda var: setattr(self, 'volume', var.value))
        service.subscribe_for_variable('Mute',
                callback=lambda var: setattr(self, 'muted',
                        means_true(var.value)))

    def disconnect(self):
        pass

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print "%s UID_OF_DEVICE" % sys.argv[0]
        sys.exit(1)

    from twisted.internet import reactor
    from twisted.internet import task

    from coherence.base import Coherence
    from coherence.upnp.devices.control_point import ControlPoint

    coherence = Coherence({'logmode':'warning'})
    ctp = ControlPoint(coherence, auto_client=['MediaRenderer'])

    client = MediaRendererClient(coherence)

    def observe():
        print client.__dict__

    #uid = sys.argv[0]
    def found_one(device=None, udn=None):
        if device:
            client.connect(device)
        elif udn:
            client.connect(coherence.get_device_with_id(udn))

    #reactor.callLater(0.2, client.connect, uid)
    ctp.connect(found_one, 'Coherence.UPnP.ControlPoint.MediaRenderer.detected')
    task.LoopingCall(observe).start(1.0)
    reactor.run()