#!/usr/bin/python

import os
import os.path
import shutil
import urllib2
import contextlib

from bs4 import BeautifulSoup

class Radio(object):
    def __init__(self):
        # might add the object to the list or something
        pass

    def update(self):
        raise NotImplementedError('update')

    def cleanup(self):
        # unused now but will be used to handle both station removal and network errors:
        #   cwd('tmp')
        #   station.update() #exception is thrown on error
        #   cwd(orig_wd)
        #   station.cleanup()
        #   move_files_from_tmp_to_cwd
        raise NotImplementedError('cleanup')

    @staticmethod
    def download_playlist(url, dest):
        if not os.path.isdir(os.path.dirname(dest)):
            os.makedirs(os.path.dirname(dest))

        print '{0} -> {1}'.format(url, dest)

        try:
            with contextlib.closing(urllib2.urlopen(url, timeout=5)) as i, open(dest, 'w') as o:
                while True:
                    chunk = i.read(8192)
                    if not chunk:
                        break
                    o.write(chunk)
        except urllib2.URLError as e:
            print 'Unable to download: {0}'.format(e)

class PlsRadio(Radio):
    def __init__(self, url, name):
        self.url = url
        self.dest = os.path.join('by-name', name)
        super(PlsRadio, self).__init__()

    def cleanup(self):
        os.unlink(self.dest)

    def update(self):
        self.download_playlist(self.url, self.dest)

class ScrapRadio(Radio):
    def __init__(self, name, url, pls_ext='.pls'):
        self.namedir = os.path.join('by-name', name)
        self.url = url
        self.pls_ext = pls_ext
        super(Radio, self).__init__()

    def cleanup(self):
        shutil.rmtree(self.namedir)

    def update(self):
        self.html = urllib2.urlopen(self.url, timeout=5).read()
        soup = BeautifulSoup(self.html)

        for (url, name) in self.scrape(soup):
            dest = os.path.join(self.namedir, name + self.pls_ext)
            self.download_playlist(url, dest)

    def scrape(self):
        # needs to return iterable of tuples (url, stationname)
        raise NotImplementedError('scrape')

class DiFm(ScrapRadio):
    def __init__(self):
        super(DiFm, self).__init__('di.fm', 'http://www.di.fm/')

    def scrape(self, soup):
        for li in soup.find_all(attrs={'data-channel-key': True}):
            channel_key = li['data-channel-key']
            src = 'http://listen.di.fm/public3/{0}.pls'.format(channel_key)
            yield (src, channel_key)

class SomaFm(ScrapRadio):
    def __init__(self):
        super(SomaFm, self).__init__('somafm.com', 'http://somafm.com/')

    def scrape(self, soup):
        div_stations = soup.find('div', id='stations')
        for anchor in div_stations.find_all('a'):
            name = anchor['href'].strip('/')
            src = 'http://somafm.com/{0}.pls'.format(name)
            yield (src, name)


stations = \
[
    # somafm.com
    SomaFm(),

    # di.fm
    DiFm(),

    # divbyzero.de
    PlsRadio('http://divbyzero.de/chill.pls', 'divbyzero.de/ambient-and-downbeat.pls'),
    PlsRadio('http://divbyzero.de/mix.pls',   'divbyzero.de/mixes-and-livesets.pls'),
    PlsRadio('http://divbyzero.de/va.pls',    'divbyzero.de/progressive.pls'),
    PlsRadio('http://divbyzero.de/old.pls',   'divbyzero.de/goa.pls'),

    # radio23.cz
    PlsRadio('http://stream1.radio23.cz/1ch128.m3u', 'radio23.cz/ch1-tekno.m3u'),
    PlsRadio('http://stream1.radio23.cz/2ch128.m3u', 'radio23.cz/ch2-breakbeat.m3u'),
    PlsRadio('http://stream1.radio23.cz/3ch128.m3u', 'radio23.cz/ch3-psytrance.m3u'),
    PlsRadio('http://stream1.radio23.cz/4ch128.m3u', 'radio23.cz/ch4-dnb.m3u'),
    PlsRadio('http://stream1.radio23.cz/5ch128.m3u', 'radio23.cz/ch5-hardcore.m3u'),
    PlsRadio('http://stream1.radio23.cz/live.m3u',   'radio23.cz/ch-live.m3u'),

    # rozhlas.cz
    PlsRadio('http://www.play.cz/radio/cro1-128.mp3.m3u',         'rozhlas.cz/1.m3u'),
    PlsRadio('http://www.play.cz/radio/cro2-128.mp3.m3u',         'rozhlas.cz/2.m3u'),
    PlsRadio('http://www.play.cz/radio/cro3-128.mp3.m3u',         'rozhlas.cz/3.m3u'),
    PlsRadio('http://www.play.cz/radio/cro7-128.mp3.m3u',         'rozhlas.cz/7.m3u'),
    PlsRadio('http://www.play.cz/radio/crobrno128.mp3.m3u',       'rozhlas.cz/brno.m3u'),
    PlsRadio('http://www.play.cz/radio/crocb128.mp3.m3u',         'rozhlas.cz/cb.m3u'),
    PlsRadio('http://www.play.cz/radio/croddur-128.mp3.m3u',      'rozhlas.cz/ddur.m3u'),
    PlsRadio('http://www.play.cz/radio/crohk128.mp3.m3u',         'rozhlas.cz/hk.m3u'),
    PlsRadio('http://www.play.cz/radio/crojuniormaxi128.mp3.m3u', 'rozhlas.cz/juniormaxi.m3u'),
    PlsRadio('http://www.play.cz/radio/crojuniormini128.mp3.m3u', 'rozhlas.cz/juniormini.m3u'),
    PlsRadio('http://www.play.cz/radio/crokv128.mp3.m3u',         'rozhlas.cz/kv.m3u'),
    PlsRadio('http://www.play.cz/radio/croliberec128.mp3.m3u',    'rozhlas.cz/liberec.m3u'),
    PlsRadio('http://www.play.cz/radio/crool128.mp3.m3u',         'rozhlas.cz/ol.m3u'),
    PlsRadio('http://www.play.cz/radio/croov128.mp3.m3u',         'rozhlas.cz/ov.m3u'),
    PlsRadio('http://www.play.cz/radio/cropardubice128.mp3.m3u',  'rozhlas.cz/pardubice.m3u'),
    PlsRadio('http://www.play.cz/radio/croplus128.mp3.m3u',       'rozhlas.cz/plus.m3u'),
    PlsRadio('http://www.play.cz/radio/croplzen128.mp3.m3u',      'rozhlas.cz/plzen.m3u'),
    PlsRadio('http://www.play.cz/radio/croregina128.mp3.m3u',     'rozhlas.cz/regina.m3u'),
    PlsRadio('http://www.play.cz/radio/croregion128.mp3.m3u',     'rozhlas.cz/region.m3u'),
    PlsRadio('http://www.play.cz/radio/crosever128.mp3.m3u',      'rozhlas.cz/sever.m3u'),
    PlsRadio('http://www.play.cz/radio/crovysocina128.mp3.m3u',   'rozhlas.cz/vysocina.m3u'),
    PlsRadio('http://www.play.cz/radio/crowave-128.mp3.m3u',      'rozhlas.cz/wave.m3u'),

    PlsRadio('http://www.bassdrive.com/v2/streams/BassDrive.pls',  'bassdrive.pls'),
    PlsRadio('http://www.dirtlabaudio.com/listen.m3u',             'dirt-lab-audio.m3u'),

    # psytube.at
    PlsRadio('http://62.75.229.17:10120/listen.pls',   'psytube.at/orochill.pls'),
    PlsRadio('http://62.75.229.17:9120/listen.pls',    'psytube.at/goa.pls'),
    PlsRadio('http://212.186.29.215:16150/listen.pls', 'psytube.at/suomi.pls'),
    PlsRadio('http://212.186.29.215:17150/listen.pls', 'psytube.at/zenonesque.pls'),
    PlsRadio('http://62.75.229.17:8120/listen.pls',    'psytube.at/dark-psy.pls'),
    PlsRadio('http://212.186.29.215:19150/listen.pls', 'psytube.at/hightech-psycore.pls'),
    PlsRadio('http://62.75.229.17:12120/listen.pls',   'psytube.at/dubstep.pls'),
    PlsRadio('http://62.75.229.17:11120/listen.pls',   'psytube.at/dnb.pls'),
    PlsRadio('http://dl.dropbox.com/s/58mmxvamha6vine/MINIMAL%20on%20www.psytube.at.pls?dl=1',   'psytube.at/minimal.pls'),
    PlsRadio('http://dl.dropbox.com/s/si0kx3x0wdg9psx/TECHNO%20on%20www.psytube.at.pls?dl=1',    'psytube.at/techno.pls'),
    PlsRadio('http://dl.dropbox.com/s/mad1dwfwt7w6u2h/FuLL%20ON%20on%20www.psytube.at.pls?dl=1', 'psytube.at/full-on.pls'),
    PlsRadio('http://dl.dropboxusercontent.com/s/jj5pygmxvmdic6w/Progressive%20on%20www.psytube.at.pls?token_hash=AAF2IT6nnJ-7QH6Sa0YOLsHzd5zli6ZT5woVasKwnqJIvQ&dl=1', 'psytube.at/progressive.pls'),

    PlsRadio('http://radior.video.muni.cz:8000/FSS_mp3-128.mp3.m3u', 'radio-R.m3u'),

    PlsRadio('http://www.play.cz/radio/ethno128.asx',  'ethno.asx'),
    PlsRadio('http://stream.laut.fm/bitfunker.m3u',    'bitfunker.m3u'),
    PlsRadio('http://app1.enation.fm/pls',             'enationFM.pls'),

    # rtvs.sk (http://live.slovakradio.sk:8000/)
    # curl -s http://live.slovakradio.sk:8000/ | grep -oP '/.+256\.mp3.m3u'
    'http://live.slovakradio.sk:8000/FM_256.mp3.m3u':         'by-name/rtvs.sk/radio_fm.m3u',
    'http://live.slovakradio.sk:8000/Devin_256.mp3.m3u':      'by-name/rtvs.sk/devin.m3u',
    'http://live.slovakradio.sk:8000/Junior_256.mp3.m3u':     'by-name/rtvs.sk/junior.m3u',
    'http://live.slovakradio.sk:8000/Klasika_256.mp3.m3u':    'by-name/rtvs.sk/klasika.m3u',
    'http://live.slovakradio.sk:8000/Litera_256.mp3.m3u':     'by-name/rtvs.sk/litera.m3u',
    'http://live.slovakradio.sk:8000/Patria_256.mp3.m3u':     'by-name/rtvs.sk/patria.m3u',
    'http://live.slovakradio.sk:8000/RSI_256.mp3.m3u':        'by-name/rtvs.sk/rsi.m3u',
    'http://live.slovakradio.sk:8000/Regina_BA_256.mp3.m3u':  'by-name/rtvs.sk/regina_ba.m3u',
    'http://live.slovakradio.sk:8000/Regina_BB_256.mp3.m3u':  'by-name/rtvs.sk/regina_bb.m3u',
    'http://live.slovakradio.sk:8000/Regina_KE_256.mp3.m3u':  'by-name/rtvs.sk/regina_ke.m3u',
    'http://live.slovakradio.sk:8000/Slovensko_256.mp3.m3u':  'by-name/rtvs.sk/slovensko.m3u',

    # radiotunguska.com
    PlsRadio('http://stream1.radiostyle.ru/play.php?pltype=m3u&media=http://stream1.radiostyle.ru:8001/tunguska', 'tunguska.m3u')
]


for radio in stations:
    radio.update()
