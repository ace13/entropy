# -*- coding: utf-8 -*-
"""

    @author: Fabio Erculiani <lxnay@sabayon.org>
    @contact: lxnay@sabayon.org
    @copyright: Fabio Erculiani
    @license: GPL-2

    B{Entropy Services Testing Command Interface}.

"""
from entropy.services.skel import SocketCommands

class Test(SocketCommands):

    def __init__(self, HostInterface):

        SocketCommands.__init__(self, HostInterface, inst_name = "test-commands")
        self.raw_commands = ['test:echo']

        self.valid_commands = {
            'test:echo': {
                'auth': False,
                'built_in': False,
                'cb': self.docmd_echo,
                'args': ["myargs"],
                'as_user': False,
                'desc': "print arguments echo",
                'syntax': "<SESSION_ID> test:echo <raw_data>",
                'from': str(self),
            },
        }


    def docmd_echo(self, myargs):

        if not myargs:
            return None, 'wrong arguments'

        return True, ' '.join(myargs)

