"""God ljudmiljö i stationsnära samhällen, webserver that implements a demonstrator.

This version is browser only where the web browser plays the videos
as well as the sounds. 

The only browser that is tested is Chrome.
"""
import platform
import argparse
import time
import json
import os
import re
import threading
import subprocess
import random
import flask
from flask import Flask, request, make_response, render_template

if 'Windows' in platform.system():
    import win32com.client
    import pythoncom
    sys_start = 'C:\ProgramData\Microsoft\Windows\Start Menu\Programs'
    home = 'C:\ProgramData\Microsoft\Windows\Start Menu Places\Personal Folder'
    user_start = os.path.join(home, 'AppData', 'Roaming', 'Microsoft', 
                              'Windows', 'Start Menu', 'Programs')
    start_dirs = [sys_start, user_start]
    prog_dirs = ['C:\Program Files\Google\Chrome\Application\chrome.exe',
                 'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe']

__version__ = '0.1.1'

app_dir = os.path.dirname(os.path.realpath(__file__))

img_dir = os.path.normpath('static/media/img')
snd_dir = os.path.normpath('static/media/audio/')
video_dir = os.path.normpath('static/media/video/')

verbose = False
debug = False

app = Flask(__name__)
sns = None

class SNS(object):
    
    def __init__(self):
        self.load_configuration()
        self.scan_audio_files()
        self.audio_ext = '.mp3' # or '.ogg'
        self.train_idx = 0
        self.abatment_idx = 0
        self.distance_idx = 0
        self.height_idx = 0

    def load_configuration(self):
        with open('config.json', 'r', encoding='utf-8') as f:
            self.config = json.load(f)

    def scan_audio_files(self):
        pattern_1 = re.compile('^s_([A-Za-z0-9]*)_(.*)_rd([0-9\.]*)m_rh([0-9\.]*)m')
        pattern_2 = re.compile('^s_([A-Za-z0-9]*)_rd([0-9\.]*)m_rh([0-9\.]*)m_(.*)$')
        l = []
        for f in os.listdir(os.path.join(app_dir, snd_dir)):
            fn, fext = os.path.splitext(f)
            img = os.path.exists(os.path.join(app_dir, img_dir, fn[2:] + '.eps'))
            if fext == '.mp3':
                try:
                    r = re.match(pattern_1, fn)
                    if r is None:
                        r = re.match(pattern_2, fn)
                        l.append({ 
                            'audio': fn,
                            'img': img, 
                            'train': r.group(1),
                            'abat': r.group(4),
                            'dist': r.group(2),
                            'height': r.group(3)
                        })
                    else:
                        l.append({
                            'audio': fn,
                            'img': img,    
                            'train': r.group(1),
                            'abat': r.group(2),
                            'dist': r.group(3),
                            'height': r.group(4)
                        })
                except:
                    print('Sorry can\'t parse filename: {}'.format(fn))

        self.audio_files = l
        self.abat_types = set([f['abat'] for f in self.audio_files])
        self.train_types = set([f['train'] for f in self.audio_files])
        
        self.distances = [float(d) for d in set([f['dist'] for f in self.audio_files])]
        self.distances.sort()
        self.heights = [float(h) for h in set([f['height'] for f in self.audio_files])]
        self.heights.sort()
        
        trains = {}
        for t in self.train_types:
            trains[t] = list(filter(lambda f: f['train'] == t, self.audio_files))
        
        self.train_data = {}        
        for train in self.train_types:
            abat = set([t['abat'] for t in trains[train]])
            tam = {}
            for t in trains[train]:
                i = {'dist': float(t['dist']),
                     'height': float(t['height']),
                     'img': t['img'],
                     'audio': t['audio']
                    }
                if t['abat'] in tam:
                    tam[t['abat']].append(i)
                else:
                    tam[t['abat']] = [i]

            self.train_data[train] = tam
            
        if verbose:
            print('SNS.scan_audio_files train_data:\n{}\n'.format(self.train_data))
        if debug:
            with open('debug_info.json', 'w') as f:
                json.dump(self.train_data, f)
            
        self.train_video = {}
        for train in self.config['trains']:
            self.train_video[train['id']] = train['video']

    def train_id(self):
        return self.config['trains'][self.train_idx]['id']
    
    def abatment_id(self):
        return self.config['abatments'][self.abatment_idx]['id']
    
    def find_item(self, train, abatment, dist, height):
        if verbose:
            print('SNS.find_item(train: {} abatment: {}, dist: {} height: {})'.format(train, abatment, dist, height))
        if abatment in self.train_data[train]:
            r = [i for i in self.train_data[train][abatment] if i['dist'] == dist and i['height'] == height]
        else:
            r = self.train_data[train]['no_abat']
        if len(r) > 0:
            r = r[0] 
        else: 
            raise Exception('No item found: {}'.format((train, abatment, dist, height))) 
        if verbose: 
            print('SNS.find_item -> {}'.format(r))
        return r
    
    def get_abatments(self, train):
        return [i for i in self.train_data[train]]

    def train_abatments_options(self, train_id):
        train_abats = list(self.train_data[train_id].keys())
        abats = [ a['id'] for a in self.config['abatments']]
        l = []
        for i,a in enumerate(abats):
            if a in train_abats:
                l.append(i)
        return l

    def video_file(self, train_id, abatment, distance=30, height=0):
        return self.train_video[train_id]
        
    def responce_data(self, abatment_info=False):
        if verbose:
            print('SNS.responce_data(train_idx: {} abat_idx dist: {} height: {})'
                  .format(self.train_idx, self.abatment_idx, self.distance_idx, self.height_idx))

        train = self.train_id()
        abatment = self.abatment_id()
        options = self.dig_out_options()
        
        
        # quick fix, if only one distance (and height) is avalable change the selection
        if len(options[0]) == 1:
            self.distance_idx = options[4]
            self.height_idx = options[5]

        distance = self.distances[self.distance_idx]  
        #distance = self.config['distances'][self.distance_idx]  
        height = self.heights[self.height_idx]
        #height = self.config['heights'][self.height_idx]
        item = self.find_item(train, abatment, distance, height)
        
        audio =  os.path.join('/', snd_dir , item['audio'] + self.audio_ext)
        video =  os.path.join('/', video_dir , self.video_file(train, abatment, distance , height))
        
        if abatment_info:
            abat = self.config['abatments'][self.abatment_idx]['type']
            abatment_text = self.config['abatment_info'][abat]
        else:
            abatment_text = ""

        jdata =  json.dumps( { 'video' : video,
                                'audio' : audio,
                                'distance' : distance,
                                'height' : height,
                                'abatment' : abatment_text,
                                'options' : options
                            })
        if verbose: 
            print('responce_data ->\n{}'.format(jdata))
        return jdata
    
    def dig_out_options(self):
        """Returns the possible option in selecting distance and heights.
        This is a quick fix, it assumes that all combination of distance and height is
        avalable or only one of each.
        """
        tdata = self.train_data[self.train_id()]
        opts = tdata.get(self.abatment_id(),[])
        if len(opts) > 1:
            dists = [i for i in range(len(self.config['distances']))]
            heights = [i for i in range(len(self.config['heights']))]
        else:
            self.distance_idx = 0
            self.height_idx = 0
            dists = [0]
            heights = [0]
        dists_selection = 0
        heights_selection = 0
        
        abats = self.train_abatments_options(self.train_id())
        abats_selection = self.abatment_idx
        if not abats_selection in abats:
            self.abatment_idx = abats[0]
            abats_selection = abats[0]
        opt = (abats, dists, heights, abats_selection, dists_selection, heights_selection)
        if debug:
            print('dig_out_options abatment_idx: {}'.format(self.abatment_idx))
            print('dig_out_options -> {}'.format(opt))
        return opt

@app.route('/')
def main_page():
    if debug:
        print('/main___________________________________________________________________________')
    train = 0
    action = 0
    response = make_response(flask.render_template('index.html',config=sns.config))
    #response.headers["Content-Type"] = "application/json"
    #response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate" # HTTP 1.1.
    #response.headers["Pragma"] = "no-cache" # HTTP 1.0.
    #response.headers["Expires"] = "0" # Proxies.
    return response

@app.route('/info1')
def info_page():
    if debug:
        print('/info1__________________________________________________________________________')
    response = make_response(flask.render_template('info1.html',config=sns.config))
    return response

@app.route('/info2')
def info2_page():
    if debug:
        print('/info2__________________________________________________________________________')
    response = make_response(flask.render_template('info2.html',config=sns.config))
    return response

@app.route('/nytta')
def nytta_page():
    if debug:
        print('/nytta__________________________________________________________________________')
    response = make_response(flask.render_template('nytta.html',config=sns.config))
    return response

@app.route('/train',methods=['GET', 'POST'] )
def train_select():
    if debug:
        print('/train__________________________________________________________________________')
    sns.train_idx = int(request.args.get('index'))
    return sns.responce_data()

@app.route('/abatment', methods=['GET', 'POST'])
def abatment_select():
    if debug:
        print('/abatmen_________________________________________________________________________')
    sns.abatment_idx = int(request.args.get('index'))
    return sns.responce_data(abatment_info=True)

@app.route('/distance',methods=['GET', 'POST'] )
def distance_select():
    if debug:
        print('/distance________________________________________________________________________')
    sns.distance_idx = int(request.args.get('index'))
    return sns.responce_data()

@app.route('/height',methods=['GET', 'POST'] )
def height_select():
    if debug:
        print('/height__________________________________________________________________________')
    sns.height_idx = int(request.args.get('index'))
    return sns.responce_data()

# for debugging
@app.route('/wb/<int:id>')
def wb(id):
    #rep.muteAll()
    return flask.render_template('wb{}.html'.format(id))

@app.route('/version')
def versions():
    s = ("sns_demo version: {}<br>python version: {}<br>flask version: {}"
        .format(__version__,
                platform.python_version(),
                flask.__version__
                    ))
    return s

def find_program(name):
    name_ = name.lower()
    if 'Windows' in platform.system():
        for prog in prog_dirs:
            if os.path.exists(prog):
                return prog
        for start_dir in start_dirs:
            for d in os.listdir(start_dir):
                if name_ in d.lower():
                    cmd = os.path.join(start_dir,d)
                    shell = win32com.client.Dispatch("WScript.Shell")
                    shortcut = shell.CreateShortCut(cmd)
                    return shortcut.Targetpath

    for d in os.get_exec_path():
        if os.path.isdir(d):
            for prog in os.listdir(d):
                if name_ in prog.lower():
                    return os.path.join(os.path.abspath(d), prog)

def start_browser(*args):
    if 'Windows' in platform.system():
        pythoncom.CoInitialize()
    b = None
    s = platform.system()
    if 'Linux' in s:
        b = 'chromium'
    elif 'Windows' in s:
        b = 'chrome'
    prog = find_program(b)
    if prog is None:
        raise Exception('Browser (Chrome) not fined for this system!\n install Google Chrome an try again!')
    cmd = [prog]
    cmd.extend(args)
    subprocess.call(cmd)
    
if __name__ == "__main__":

    def int_or_str(text):
        """Helper function for argument parsing."""
        try:
            return int(text)
        except ValueError:
            return text
    
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-v', '--verbose', action="store_true",
                        help='Verbose mode, prints program information while running.')
    parser.add_argument('-d', '--debug', action="store_true",
                        help='Debug mode, prints program information while running.')

    args = parser.parse_args()
    if args.debug:
        verbose = True
        debug = True
    if not debug:
        verbose = args.verbose

    if verbose: print('Restart_________________________________________________________________________')    
    if verbose: print('Python version: {}'.format(platform.python_version()))
    if verbose: print('Flask version: {}'.format(flask.__version__))
    sns = SNS()
    if verbose: print('config.json:\n', sns.config)

    port = 5000
    url = "http://127.0.0.1:{0}".format(port)

    threading.Timer(1.25, lambda: start_browser(url) ).start()

    app.run(host='127.0.0.1', port=port, debug=debug)
