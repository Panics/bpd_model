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
import random

# ------------------------------------------------------------------------------------------------------------
_oscServerIP:str = "127.0.0.1"
_oscServerListenPort:int = 2323
_oscMessageDestinationIP = "127.0.0.1"
_oscMessageDestinationPort = 2324

# ------------------------------------------------------------------------------------------------------------
class ModelOutputData:
    _bpdValue:float

    @property
    def BpdValue(self):
        return self._bpdValue
    
    @BpdValue.setter
    def BpdValue(self, val):
        self._bpdValue = val
    
    def __init__(self):
        self._bpdValue = 0

# ------------------------------------------------------------------------------------------------------------
_oscDispatcher:Dispatcher = Dispatcher()
_oscServer:AsyncIOOSCUDPServer
_oscTransport:BaseTransport
_oscProtocol:DatagramProtocol
_oscClient:SimpleUDPClient = SimpleUDPClient(_oscMessageDestinationIP, _oscMessageDestinationPort)
_modelOutputData:ModelOutputData = ModelOutputData()
_timeLoop:Timeloop = Timeloop()
_bpdModelUpdateCounter:int = 0

# ------------------------------------------------------------------------------------------------------------
def handleOscMessage_Angle(address, *args):
    print(f"{address}: {args}")

# ------------------------------------------------------------------------------------------------------------
def handleOscMessage_Gyro(address, *args):
    print(f"{address}: {args}")

# ------------------------------------------------------------------------------------------------------------
def handleOscMessage_Accel(address, *args):
    print(f"{address}: {args}")

# ------------------------------------------------------------------------------------------------------------
def handleOscMessage_AccelAngle(address, *args):
    print(f"{address}: {args}")

# ------------------------------------------------------------------------------------------------------------
def handleOscMessage_AccelTemp(address, *args):
    print(f"{address}: {args}")

# ------------------------------------------------------------------------------------------------------------
@_timeLoop.job(interval=timedelta(seconds=1))
def sendOscMessages():
    global _oscClient
    global _bpdModelUpdateCounter
    _oscClient.send_message("/Brandeis/BPD/Model", _modelOutputData.BpdValue)
    print(f"sendOscMessages: {time.ctime()}, BPD model value: {_modelOutputData.BpdValue}, Number of BPD model updates: {_bpdModelUpdateCounter}")
    _bpdModelUpdateCounter = 0

# ------------------------------------------------------------------------------------------------------------
@_timeLoop.job(interval=timedelta(seconds=0.1))
def updateBPDModel():
    global _modelOutputData
    global _bpdModelUpdateCounter
    _modelOutputData.BpdValue = random.uniform(-1,1)
    _bpdModelUpdateCounter += 1
#    print(f"updateBPDModel: {time.ctime()}, {_modelOutputData.BpdValue}")

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

    print('Mapping osc message handlers')
    _oscDispatcher.map("/Brandeis/BPD/SendAngle", handleOscMessage_Angle) 
    _oscDispatcher.map("/Brandeis/BPD/SendGyro", handleOscMessage_Gyro) 
    _oscDispatcher.map("/Brandeis/BPD/SendAccel", handleOscMessage_Accel) 
    _oscDispatcher.map("/Brandeis/BPD/SendAccelAngle", handleOscMessage_AccelAngle) 

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
    print('Exiting init_main()')


# ------------------------------------------------------------------------------------------------------------

print('Initializing Main')

asyncio.run(mainInit())
 
print('All done!')