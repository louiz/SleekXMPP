#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Slixmpp: The Slick XMPP Library
    Copyright (C) 2015 Emmanuel Gil Peyrot
    This file is part of Slixmpp.

    See the file LICENSE for copying permission.
"""

import sys

import logging
from getpass import getpass
from argparse import ArgumentParser

import slixmpp
from slixmpp.exceptions import XMPPError
from slixmpp import asyncio

log = logging.getLogger(__name__)


class AskConfirm(slixmpp.ClientXMPP):

    """
    A basic client asking an entity if they confirm the access to an HTTP URL.
    """

    def __init__(self, jid, password, recipient, id, url, method):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        self.recipient = recipient
        self.id = id
        self.url = url
        self.method = method

        # Will be used to set the proper exit code.
        self.confirmed = None

        self.add_event_handler("session_start", self.start)

    @asyncio.coroutine
    def start(self, event):
        log.info('Sending confirm request %s to %s who wants to access %s using '
                 'method %s...' % (self.id, self.recipient, self.url, self.method))
        confirmed = yield from self['xep_0070'].ask_confirm(self.recipient,
                                                            id=self.id,
                                                            url=self.url,
                                                            method=self.method,
                                                            message='Plz say yes or no for {method} {url} ({id}).')
        if confirmed:
            print('Confirmed')
        else:
            print('Denied')
        self.confirmed = confirmed
        self.disconnect()


if __name__ == '__main__':
    # Setup the command line arguments.
    parser = ArgumentParser()
    parser.add_argument("-q","--quiet", help="set logging to ERROR",
                        action="store_const",
                        dest="loglevel",
                        const=logging.ERROR,
                        default=logging.INFO)
    parser.add_argument("-d","--debug", help="set logging to DEBUG",
                        action="store_const",
                        dest="loglevel",
                        const=logging.DEBUG,
                        default=logging.INFO)

    # JID and password options.
    parser.add_argument("-j", "--jid", dest="jid",
                        help="JID to use")
    parser.add_argument("-p", "--password", dest="password",
                        help="password to use")

    # Other options.
    parser.add_argument("-r", "--recipient", required=True,
                        help="Recipient JID")
    parser.add_argument("-i", "--id", required=True,
                        help="id TODO")
    parser.add_argument("-u", "--url", required=True,
                        help="URL the user tried to access")
    parser.add_argument("-m", "--method", required=True,
                        help="HTTP method used")

    args = parser.parse_args()

    # Setup logging.
    logging.basicConfig(level=args.loglevel,
                        format='%(levelname)-8s %(message)s')

    if args.jid is None:
        args.jid = input("Username: ")
    if args.password is None:
        args.password = getpass("Password: ")

    xmpp = AskConfirm(args.jid, args.password, args.recipient, args.id,
                      args.url, args.method)
    xmpp.register_plugin('xep_0070')

    # Connect to the XMPP server and start processing XMPP stanzas.
    xmpp.connect()
    xmpp.process(forever=False)
    sys.exit(0 if xmpp.confirmed else 1)
