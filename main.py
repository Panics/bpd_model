# ------------------------------------------------------------------------------------------------------------
# Python libraries
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
from pythonosc.udp_client import SimpleUDPClient

from asyncio import BaseTransport
from asyncio import DatagramProtocol
from timeloop import Timeloop
from datetime import timedelta

import asyncio
import keyboard
import time
import os
import argparse
import sys

import matplotlib.pyplot as plt
import threading
from queue import Queue

# ------------------------------------------------------------------------------------------------------------
# Helper code
from Helpers.AbstractModel import AbstractModel
from Helpers.AbstractTreatment import AbstractTreatment
from Helpers.ModelOutputData import ModelOutputData
from Helpers.ModelPlot import ModelPlot
from Helpers.ImuData import ImuData
from Helpers.Theremin import Theremin
from Helpers.ThereminOutputData import ThereminOutputData
from Helpers.TimeKeeper import TimeKeeper
from BPDModel2ConfigurationTracker import BPDModel2ConfigurationTracker

from Sound import list_output_devices
from Sound.utils import midi_str_to_midi, midi_to_freq

# ------------------------------------------------------------------------------------------------------------
# The bpd model and treatment logic
from BPDModel2 import BPDModel2
from BPDModel2 import BPDModel2Configuration
from BPDTreatment1 import BPDTreatment1

# Instantiate the bpd model and treatment logic to use
_modelUpdateInterval:float = 0.0015
_modelToUse:BPDModel2 = BPDModel2(dt=_modelUpdateInterval, delay_seconds=0.02, g_gain=0.07, lamb=0.5)
_treatmentToUse:BPDTreatment1 = BPDTreatment1(XAngleRatio=1, XAngleVelocityRatio=0.0, TreatmentScale=0.015)
_modelConfigurationTracker:BPDModel2ConfigurationTracker = BPDModel2ConfigurationTracker()
_theremin:Theremin

# ------------------------------------------------------------------------------------------------------------
# configuration of OSC sending/receiving
_oscServerIP:str = "0.0.0.0"
_oscServerListenPort:int = 2323
_oscMessageDestinationIP = "255.255.255.255"
_oscMessageDestinationPort = 2323
_debugLogOSCActivity:bool = False
_oscSendInterval:float = 1

# ------------------------------------------------------------------------------------------------------------
_oscDispatcher:Dispatcher = Dispatcher()
_oscServer:AsyncIOOSCUDPServer
_oscTransport:BaseTransport
_oscProtocol:DatagramProtocol
_oscClient:SimpleUDPClient = SimpleUDPClient(address=_oscMessageDestinationIP, port=_oscMessageDestinationPort, allow_broadcast=True)
_timeLoop:Timeloop = Timeloop()
_timeKeeper:TimeKeeper = TimeKeeper()
_imuData:ImuData = ImuData()
_plottingQueue:Queue = Queue()
_mainIsRunning:bool = True

# ------------------------------------------------------------------------------------------------------------
def handleOscMessage_Angle(address, *args):
    global _imuData
    global _debugLogOSCActivity
    _imuData.xAngle = args[0]
    _imuData.yAngle = args[1]
    _imuData.zAngle = args[2]
    if _debugLogOSCActivity:
        print(f"Received OSC: {address}: {args}")

# ------------------------------------------------------------------------------------------------------------
def handleOscMessage_Gyro(address, *args):
    global _imuData
    global _debugLogOSCActivity
    _imuData.xGyro = args[0]
    _imuData.yGyro = args[1]
    _imuData.zGyro = args[2]
    if _debugLogOSCActivity:
        print(f"Received OSC: {address}: {args}")

# ------------------------------------------------------------------------------------------------------------
def handleOscMessage_Accel(address, *args):
    global _imuData
    global _debugLogOSCActivity
    _imuData.xAccel = args[0]
    _imuData.yAccel = args[1]
    _imuData.zAccel= args[2]
    if _debugLogOSCActivity:
        print(f"Received OSC: {address}: {args}")

# ------------------------------------------------------------------------------------------------------------
def handleOscMessage_AccelAngle(address, *args):
    global _imuData
    global _debugLogOSCActivity
    _imuData.xAccelAngle = args[0]

    _imuData.yAccelAngle = args[1]
    if _debugLogOSCActivity:
        print(f"Received OSC: {address}: {args}")

# ------------------------------------------------------------------------------------------------------------
def handleOscMessage_Temp(address, *args):
    global _imuData
    global _debugLogOSCActivity
    _imuData.temp = args[0]
    if _debugLogOSCActivity:
        print(f"Received OSC: {address}: {args}")

# ------------------------------------------------------------------------------------------------------------
@_timeLoop.job(interval=timedelta(seconds=_oscSendInterval))
def sendOscMessages():
    global _oscClient
    global _modelToUse
    global _theremin
    _oscClient.send_message("/Brandeis/BPD/Model", [_modelToUse.ModelState.BpdMood, _modelToUse.ModelState.BpdTreatmentEffect])
    print(f"Sent OSC: {time.ctime()}, BPD model mood: {_modelToUse.ModelState.BpdMood}, Treatment model effect: {_modelToUse.ModelState.BpdTreatmentEffect}")

# ------------------------------------------------------------------------------------------------------------
@_timeLoop.job(interval=timedelta(seconds=_modelUpdateInterval))
def updateBPDModel():
    global _modelToUse
    global _imuData
    global _timeKeeper

    # Update the configurationt that the model should use, based on the elapsed time
    _modelToUse.CurrentConfiguration = _modelConfigurationTracker.GetActiveConfiguration(_timeKeeper.ElapsedTimeInSeconds())

    # Update the model
    _modelToUse.step(_treatmentToUse.CalculateTreatmentEffect(_imuData), DT=_modelUpdateInterval)

    # update the theremin
    _theremin.Update(_modelToUse.ModelState)

    # Queue date for plotting (which happens in a different timeloop job that runs in parallel)
    _plottingQueue.put(_modelToUse.ModelState)

# ------------------------------------------------------------------------------------------------------------
async def mainLoop():
    global _timeLoop
    print('Starting main loop - press and hold ESC/SPACE to exit')
    _timeLoop.start()
    while(not keyboard.is_pressed('Esc') and not keyboard.is_pressed('Space')):
        await asyncio.sleep(0.1)
    _timeLoop.stop()

# ------------------------------------------------------------------------------------------------------------
def on_key(event:str):
    global _debugLogOSCActivity

    _modelToUse.on_key(event)
    _treatmentToUse.on_key(event)
    
    printMsg:bool=False
    if event.key == 'd': 
        _debugLogOSCActivity = False
        printMsg=True
    elif event.key == 'D': 
        _debugLogOSCActivity = True
        printMsg=True
    if event.key == 'x': 
        _theremin.Stop()
        printMsg=True
    elif event.key == 'X': 
        _theremin.Start()
        printMsg=True
    
    if printMsg:
        print(f"Debug log incoming OSC messages = {_debugLogOSCActivity}, Theremin is playing: {_theremin.IsPlaying}")

# ------------------------------------------------------------------------------------------------------------
async def mainInit():
    global _oscServer
    global _oscTransport
    global _oscProtocol
    global _oscDispatcher
    global _oscServerIP
    global _oscServerListenPort
    global _mainIsRunning

    print('Mapping osc message handlers')
    _oscDispatcher.map("/Brandeis/BPD/SendAngle", handleOscMessage_Angle) 
    _oscDispatcher.map("/Brandeis/BPD/SendGyro", handleOscMessage_Gyro) 
    _oscDispatcher.map("/Brandeis/BPD/SendAccel", handleOscMessage_Accel) 
    _oscDispatcher.map("/Brandeis/BPD/SendAccelAngle", handleOscMessage_AccelAngle) 
    _oscDispatcher.map("/Brandeis/BPD/SendTemp", handleOscMessage_Temp) 

    print('Starting OSC server')
    _oscServer = AsyncIOOSCUDPServer((_oscServerIP, _oscServerListenPort), _oscDispatcher, asyncio.get_event_loop())
    _oscTransport, _oscProtocol = await _oscServer.create_serve_endpoint()  # Create datagram endpoint and start serving
    print(f"OSC server is running on {_oscServerIP}:{_oscServerListenPort}")

    await mainLoop()

    print('Unmapping osc message handlers')
    _oscDispatcher.unmap("/Brandeis/BPD/SendAngle", handleOscMessage_Angle) 
    _oscDispatcher.unmap("/Brandeis/BPD/SendGyro", handleOscMessage_Gyro) 
    _oscDispatcher.unmap("/Brandeis/BPD/SendAccel", handleOscMessage_Accel) 
    _oscDispatcher.unmap("/Brandeis/BPD/SendAccelAngle", handleOscMessage_AccelAngle) 
    print('Stopping osc server')
    _oscTransport.close()  # Clean up serve endpoint
    _mainIsRunning = False
    print('Exiting init_main()')

# ------------------------------------------------------------------------------------------------------------
def run_event_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(mainInit())

# ------------------------------------------------------------------------------------------------------------
def runPlotter():
    print('Entering runPlotter()')
    modelPlot:ModelPlot = ModelPlot()
    
    modelPlot.Fig.canvas.mpl_connect('key_press_event', on_key)

    while _mainIsRunning:
        if not _plottingQueue.empty():
            message:ModelOutputData = _plottingQueue.get()
            modelPlot.UpdatePlot(message)
        plt.pause(_modelUpdateInterval)
    print('Exiting runPlotter()')

# ------------------------------------------------------------------------------------------------------------
def parse_args(args):
    parser = argparse.ArgumentParser(
            prog='main.py',
            description='BPD Simulator. Simulates BPD Mood, while deriving Treatment effectiveness as a model input from incoming OSC messages from an Arduino controlled IMU.\n',
            epilog='\n------------\nEpilog here\n',
            formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('--list-audio-outputs', '-l', dest='list_audio_outputs', required=False,
            action='store_true', help='List the available audio output devices')
    parser.add_argument('--audio-output', '-o', dest='audio_output', required=False,
            type=int, help='Select an output audio device by index (see -l)')
    parser.add_argument('--audio-backend', '-b', dest='audio_backend', required=False, default='portaudio',
            help='Select the audio backend (default: portaudio). Supported: ' +
            '{"portaudio", "jack", "coreaudio"}')
    parser.add_argument('--channels', '-c', dest='channels', required=False, type=int, default=2,
            help='Number of audio channels (default: 2)')
    parser.add_argument('--rate', '-r', dest='sampling_rate', required=False, type=int, default=44100,
            help='Sampling rate (default: 44100 Hz)')
    parser.add_argument('--discrete', '-d', dest='discrete', required=False, action='store_true',
            help='If set then discrete notes will be generated instead of samples over a continuous ' +
            'frequency space (default: false)')
    parser.add_argument('--generator', '-g', dest='generator', required=False,
            default='SineLoop', help='Wave generator to be used. See ' +
            'http://ajaxsoundstudio.com/pyodoc/api/classes/generators.html. ' +
            'Default: SineLoop')
    parser.add_argument('--min-frequency', dest='min_frequency', required=False, type=int, default=55,
            help='Minimum audio frequency (default: 55 Hz)')
    parser.add_argument('--max-frequency', dest='max_frequency', required=False, type=int, default=5000,
            help='Maximum audio frequency (default: 5 kHz)')
    parser.add_argument('--min-note', dest='min_note', required=False, type=str, default=None,
            help='Minimum MIDI note, as a string (e.g. A4)')
    parser.add_argument('--max-note', dest='max_note', required=False, type=str, default=None,
            help='Maximum MIDI note, as a string (e.g. A4)')

    parser.print_help()
    print()
    opts, args = parser.parse_known_args(args)
    return opts, args

# ------------------------------------------------------------------------------------------------------------
def SetupModelConfigurations():
    global _modelConfigurationTracker

    # add an example configuration, active from t=0 seconds to t=10 seconds
    _modelConfigurationTracker.AddConfiguration(
                                                startTimeSeconds=0,
                                                endTimeSeconds=10,
                                                configuration = BPDModel2Configuration(
                                                    g1=3.0, 
                                                    g2=3.0,
                                                    qPmin=10.0, 
                                                    qPmax=10.0,
                                                    qNmin=2.5, 
                                                    qNmax=7.0,
                                                    lamb=4,
                                                    dt=0.001,
                                                    tmin=1.0, 
                                                    tmax=5.0,
                                                    injectMode='tilt_to_PN',
                                                    delay_seconds=0.02,
                                                    g_gain=0.2                                                    
                                                )
                                                )

    # add an example configuration, active from t=10 seconds to t=20 seconds
    _modelConfigurationTracker.AddConfiguration(
                                                startTimeSeconds=10,
                                                endTimeSeconds=20,
                                                configuration = BPDModel2Configuration(
                                                    g1=3.0, 
                                                    g2=3.0,
                                                    qPmin=10.0, 
                                                    qPmax=10.0,
                                                    qNmin=2.5, 
                                                    qNmax=7.0,
                                                    lamb=4,
                                                    dt=0.001,
                                                    tmin=1.0, 
                                                    tmax=5.0,
                                                    injectMode='tilt_to_PN',
                                                    delay_seconds=0.02,
                                                    g_gain=0.2                                                    
                                                )
                                                )
    
    # beyond t=20 seconds, or in general, if no 'active' model configuration has been found, a default BPModel2Configuration will be used

    _modelConfigurationTracker.PrintConfigurationInfo()

# ------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    # clear screen
    os.system('cls' if os.name == 'nt' else 'clear')

    args = sys.argv[1:]
    opts, args = parse_args(args)

    if opts.min_note:
        opts.min_frequency = midi_to_freq(midi_str_to_midi(opts.min_note))
    if opts.max_note:
        opts.max_frequency = midi_to_freq(midi_str_to_midi(opts.max_note))

    if opts.list_audio_outputs:
        list_output_devices()
        exit()

    # print keys that the scripts respond to
    print(f'Listing keys:')
    print(f'=============')
    _modelToUse.print_key_info()
    _treatmentToUse.print_key_info()
    print(f'{os.path.basename(__file__)}: d/D = debug printing incoming OSC message info off/on')      
    print(f'{os.path.basename(__file__)}: x/X = Theremin sound generation off/on')      
    print()
    input('Press ENTER to continue...')
    print()

    SetupModelConfigurations()

    print('Instantiating Theremin')
    # create sound generator based on command line properties
    _theremin=Theremin(wave=opts.generator, audio_backend=opts.audio_backend, discrete=opts.discrete, min_frequency=opts.min_frequency, max_frequency=opts.max_frequency, audio_output=opts.audio_output, channels=opts.channels, sampling_rate=opts.sampling_rate)
    print()

    print('Initializing Main')
    new_loop = asyncio.new_event_loop()
    eventThread:threading.Thread = threading.Thread(target=run_event_loop, args=(new_loop,))
    eventThread.start()
    print()

    runPlotter()

    eventThread.join()
    print('All done!')