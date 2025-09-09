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

# ------------------------------------------------------------------------------------------------------------
# The bpd model and treatment logic
from BPDModel1 import BPDModel1
from BPDTreatment1 import BPDTreatment1

# Instantiate the bpd model and treatment logic to use
_modelToUse:AbstractModel = BPDModel1(mood=0.5, moodVelocity=0, treatmentEffect=0)
_modelUpdateInterval:float = 0.01
_treatmentToUse:AbstractTreatment = BPDTreatment1()

# ------------------------------------------------------------------------------------------------------------
# configuration of OSC sending/receiving
_oscServerIP:str = "127.0.0.1"
_oscServerListenPort:int = 2323
_oscMessageDestinationIP = "127.0.0.1"
_oscMessageDestinationPort = 2324
_debugLogIncomingOSC:bool = True
_oscSendInterval:float = 1

# ------------------------------------------------------------------------------------------------------------
_oscDispatcher:Dispatcher = Dispatcher()
_oscServer:AsyncIOOSCUDPServer
_oscTransport:BaseTransport
_oscProtocol:DatagramProtocol
_oscClient:SimpleUDPClient = SimpleUDPClient(_oscMessageDestinationIP, _oscMessageDestinationPort)
_timeLoop:Timeloop = Timeloop()

_imuData:ImuData = ImuData()
_plottingQueue:Queue = Queue()
_mainIsRunning:bool = True

# ------------------------------------------------------------------------------------------------------------
def handleOscMessage_Angle(address, *args):
    global _imuData
    global _debugLogIncomingOSC
    _imuData.xAngle = args[0]
    _imuData.yAngle = args[1]
    _imuData.zAngle = args[2]
    if _debugLogIncomingOSC:
        print(f"Received OSC: {address}: {args}")

# ------------------------------------------------------------------------------------------------------------
def handleOscMessage_Gyro(address, *args):
    global _imuData
    global _debugLogIncomingOSC
    _imuData.xGyro = args[0]
    _imuData.yGyro = args[1]
    _imuData.zGyro = args[2]
    if _debugLogIncomingOSC:
        print(f"Received OSC: {address}: {args}")

# ------------------------------------------------------------------------------------------------------------
def handleOscMessage_Accel(address, *args):
    global _imuData
    global _debugLogIncomingOSC
    _imuData.xAccel = args[0]
    _imuData.yAccel = args[1]
    _imuData.zAccel= args[2]
    if _debugLogIncomingOSC:
        print(f"Received OSC: {address}: {args}")

# ------------------------------------------------------------------------------------------------------------
def handleOscMessage_AccelAngle(address, *args):
    global _imuData
    global _debugLogIncomingOSC
    _imuData.xAccelAngle = args[0]
    _imuData.yAccelAngle = args[1]
    _imuData.zAccelAngle= args[2]
    if _debugLogIncomingOSC:
        print(f"Received OSC: {address}: {args}")

# ------------------------------------------------------------------------------------------------------------
def handleOscMessage_Temp(address, *args):
    global _imuData
    global _debugLogIncomingOSC
    _imuData.temp = args[0]
    if _debugLogIncomingOSC:
        print(f"Received OSC: {address}: {args}")

# ------------------------------------------------------------------------------------------------------------
@_timeLoop.job(interval=timedelta(seconds=_oscSendInterval))
def sendOscMessages():
    global _oscClient
    global _modelToUse
    _oscClient.send_message("/Brandeis/BPD/Model", _modelToUse.ModelState.BpdMood)
    print(f"Sent OSC: {time.ctime()}, BPD model mood: {_modelToUse.ModelState.BpdMood}, BPD model mood velocity: {_modelToUse.ModelState.BpdMoodVelocity}, BPD model treatment effect: {_modelToUse.ModelState.BpdTreatmentEffect}")

# ------------------------------------------------------------------------------------------------------------
@_timeLoop.job(interval=timedelta(seconds=_modelUpdateInterval))
def updateBPDModel():
    global _modelToUse
    global _imuData
    _modelToUse.step(_treatmentToUse.CalculateTreatmentEffect(_imuData), DT=_modelUpdateInterval)
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

    while _mainIsRunning:
        if not _plottingQueue.empty():
            message:ModelOutputData = _plottingQueue.get()
            modelPlot.UpdatePlot(message)
        plt.pause(_modelUpdateInterval)
    print('Exiting runPlotter()')

# ------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    print('Initializing Main')
    new_loop = asyncio.new_event_loop()
    eventThread:threading.Thread = threading.Thread(target=run_event_loop, args=(new_loop,))
    eventThread.start()
    runPlotter()
    eventThread.join()
    print('All done!')