from BPDModel2Configuration import BPDModel2Configuration

class ConfigurationTimePeriod:
    _startTimeSeconds:float
    _endTimeSeconds:float
    _configuration:BPDModel2Configuration

    @property
    def StartTimeSeconds(self):
        return self._startTimeSeconds

    @property
    def EndTimeSeconds(self):
        return self._endTimeSeconds

    @property
    def Configuration(self):
        return self._configuration

    def __init__(self, configuration:BPDModel2Configuration, startTimeSeconds:float = 0, endTimeSeconds:float = 10):
        self._startTimeSeconds = startTimeSeconds
        self._endTimeSeconds = endTimeSeconds
        self._configuration = configuration


class BPDModel2ConfigurationTracker:
    _configurations:list

    _defaultConfiguration:BPDModel2Configuration

    @property
    def DefaultConfiguration(self):
        return self._defaultConfiguration

    @DefaultConfiguration.setter
    def DefaultConfiguration(self, value):
        self._defaultConfiguration = value

    def GetActiveConfiguration(self, timeSeconds:float=0) -> BPDModel2Configuration:
        tSec:float=timeSeconds
        for configuration in self._configurations:
            if configuration.StartTimeSeconds <= tSec:
                if configuration.EndTimeSeconds > tSec:
#                    print(f'Returning configuration for {configuration.StartTimeSeconds} - {configuration.EndTimeSeconds} time {tSec}')
                    return configuration.Configuration
        return self.DefaultConfiguration

    def AddConfiguration(self, configuration:BPDModel2Configuration, startTimeSeconds:float, endTimeSeconds:float):
        self._configurations.append(ConfigurationTimePeriod(configuration, startTimeSeconds, endTimeSeconds))
        
    def PrintConfigurationInfo(self):
        print(f'Listing Configurations')
        print(f'======================')
        for configuration in self._configurations:
            duration:float = configuration.EndTimeSeconds - configuration.StartTimeSeconds
            print(f'\tStart {configuration.StartTimeSeconds} End {configuration.EndTimeSeconds} Duration {duration}')
        input('Press ENTER to continue...')
        print()

    
    def __init__(self):
        self._configurations = []
        self._defaultConfiguration = BPDModel2Configuration()
