#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Scrubber for jpeg files
"""

if __name__ == "__main__":
    import sys

class ScrubJpeg:

    jfif_header_1 = '\xff\xd8\xff\xe0'
    jfif_header_2 = 'JFIF\x00'

    def __init__(self, filename):
        with open(filename, 'rb') as jpegfile:
            self.data = jpegfile.read()
        self.markers = self.build_markers(self.data)
        self.is_jfif = self.check_jfif(self.data)


    def scrub(self, filename):
        """Writes a scrubbed version of the data to filename"""
        if self.is_jfif:
            self._scrub_jfif()
        else:
            self._scrub()
        with open(filename, 'wb') as jpegfile:
            for byte in self.data:
                jpegfile.write(byte)

    def _scrub(self):
        """Scrubs unimportant data"""
        tdata = list(self.data)
        for i in xrange(len(self.markers) - 1, -1, -1):
            if self.is_marker_metadata(tdata[self.markers[i] + 1]):
                del tdata[self.markers[i]:self.markers[i + 1]]
                del self.markers[i]
        self.data = "".join(tdata)

    def _scrub_jfif(self):
        pass
    
    @staticmethod
    def check_jfif(data):
        """Returns true if data is a jfif image"""
        return data.startswith(ScrubJpeg.jfif_header_1) and \
        data[len(ScrubJpeg.jfif_header_1) + 2:].startswith(ScrubJpeg.jfif_header_2)

    @staticmethod
    def build_markers(jpegdata):
        """Returns a table of where all markers begin (points to the FF, not the marker ID)"""
        markers = []
        i = 0
        while i < len(jpegdata):
            if jpegdata[i] == '\xff' and '\x01' <= jpegdata[i + 1] <= '\xFE':
                markers.append(i)
            i += 2
        print markers
        return markers

    def is_marker_metadata(self, marker):
        """Returns true if marker indicates metadata"""
        val = ord(marker)
        msn = val >> 4
        if msn == 0xc or msn == 0xd or val == 0x3 and self.is_jfif:
            return False

        #Everything else as of now is unused or used for metadaat
        return True

if __name__ == "__main__":
    scrubber = ScrubJpeg(sys.argv[1])
    scrubber.scrub("%s-scr" % sys.argv[1])
