##
## This file is part of the libsigrokdecode project.
##
## Copyright (C) 2018 Stefan Brüns <stefan.bruens@rwth-aachen.de>
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, see <http://www.gnu.org/licenses/>.
##

import sigrokdecode as srd

class Decoder(srd.Decoder):
    api_version = 3
    id = 'counter'
    name = 'Counter'
    longname = 'Edge counter'
    desc = 'Count number of edges.'
    license = 'gplv2+'
    inputs = ['logic']
    outputs = []
    channels = (
        {'id': 'data', 'name': 'Data', 'desc': 'Data line'},
    )
    optional_channels = (
        {'id': 'reset', 'name': 'Reset', 'desc': 'Reset line'},
    )
    annotations = (
        ('edge_count', 'Count'),
        ('word_count', 'Count'),
    )
    annotation_rows = (
        ('edge_count', 'Edge', (0,)),
        ('word_count', 'Divided', (1,)),
    )
    options = (
        { 'id': 'edge', 'desc': 'Edges to check', 'default': 'any', 'values': ('any', 'rising', 'falling') },
        { 'id': 'divider', 'desc': 'Count divider', 'default': 0 },
    )

    def __init__(self):
        self.reset()

    def reset(self):
        self.edge_count = 0
        self.word_count = 0
        self.have_reset = None

    def metadata(self, key, value):
        if key == srd.SRD_CONF_SAMPLERATE:
            self.samplerate = value

    def start(self):
        self.out_ann = self.register(srd.OUTPUT_ANN)
        self.edge = self.options['edge']
        self.divider = self.options['divider']
        if self.divider < 0:
            self.divider = 0

    def put_count(self, row, count):
        self.put(self.samplenum, self.samplenum, self.out_ann,
            [row, [str(count)]])

    def decode(self):
        condition = [ {'rising':  {0: 'r'},
                       'falling': {0: 'f'},
                       'any':     {0: 'e'},}[self.edge] ]

        if self.has_channel(1):
            self.have_reset = True
            condition.append( {1: 'f'} )

        while True:
            self.wait(condition)
            if self.have_reset and self.matched[1]:
                self.edge_count = 0
                self.word_count = 0
                self.put_count(1, "R")
                continue

            self.edge_count += 1

            self.put_count(0, self.edge_count)
            if self.divider > 0 and (self.edge_count % self.divider) == 0:
                self.word_count += 1
                self.put_count(1, self.word_count)
