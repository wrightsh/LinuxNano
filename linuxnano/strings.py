class col():
    #NODE
    NAME          = 0
    TYPE_INFO     = 1
    DESCRIPTION   = 2

    #SystemNode
    BACKGROUND_SVG = 10

    #DeviceNode
    STATUS = 10

    #DeviceIconNode
    SVG       = 10
    LAYER     = 11
    X         = 12
    Y         = 13
    SCALE     = 14
    ROTATION  = 15
    HAS_TEXT  = 16
    TEXT      = 17
    TEXT_X    = 18
    TEXT_Y    = 19
    FONT_SIZE = 20
    POS       = 21



    #Value is always the value in terms of the GUI, where as there's also HAL_VALUE
    #The variables use VALUE but the Hal nodes use display_value since it's a convertred number
    #Need to keep the same (30) because we use the same display code for read only HAL and variables
    VALUE = 30
    #DISPLAY_VALUE = VALUE

    HAL_VALUE = 20 #True/False

    #HalNode
    HAL_PIN      = 40
    HAL_PIN_TYPE = 41

    #DigitalInputNode
    VALUE_OFF = 22
    VALUE_ON  = 23

    #BoolVarNode
    OFF_NAME      = 11
    ON_NAME       = 12
    OFF_ENABLE    = 13
    ON_ENABLE     = 14
    ENABLE_MANUAL = 15
    VIEW_ONLY     = 16


    #AnalogInputNode
    UNITS                   = 22
    DISPLAY_DIGITS          = 23
    DISPLAY_SCIENTIFIC      = 24
    CALIBRATION_TABLE_MODEL = 25

    #FloatVarNode
    MIN           = 11
    MAX           = 12
    ENABLE_MANUAL = 13



class typ():

    #For behavior tree (bt) editor
    SEQUENCE_NODE = 'Sequence'
    SELECTOR_NODE = 'Selector'
    WHILE_NODE = 'While'
    SET_OUTPUT_NODE = 'Set_Output'
    WAIT_TIME_NODE = 'Wait_Time'


    TOOL_NODE = 'Tool_Node'
    SYSTEM_NODE = 'System_Node'
    DEVICE_NODE = 'Device_Node'

    DEVICE_ICON_NODE =  'Device_Icon_Node'


    D_IN_NODE  = 'Digital_Input_Node'
    A_IN_NODE  = 'Analog_Input_Node'
    D_OUT_NODE = 'Digital_Output_Node'
    A_OUT_NODE = 'Analog_Output_Node'
    HAL_NODES = [D_IN_NODE, D_OUT_NODE, A_IN_NODE, A_OUT_NODE]


    BOOL_VAR_NODE = 'Bool_Var_Node'
    FLOAT_VAR_NODE = 'Float_Var_Node'

class strings():

    #For behavior tree (bt) editor
    SEQUENCE_NODE = 'Sequence'
    SELECTOR_NODE = 'Selector'
    WHILE_NODE = 'While'
    SET_OUTPUT_NODE = 'Set_Output'
    WAIT_TIME_NODE = 'Wait_Time'


    TOOL_NODE = 'Tool_Node'
    SYSTEM_NODE = 'System_Node'
    DEVICE_NODE = 'Device_Node'

    DEVICE_ICON_NODE =  'Device_Icon_Node'


    D_IN_NODE  = 'Digital_Input_Node'
    A_IN_NODE  = 'Analog_Input_Node'
    D_OUT_NODE = 'Digital_Output_Node'
    A_OUT_NODE = 'Analog_Output_Node'
    HAL_NODES = [D_IN_NODE, D_OUT_NODE, A_IN_NODE, A_OUT_NODE]


    BOOL_VAR_NODE = 'Bool_Var_Node'
    FLOAT_VAR_NODE = 'Float_Var_Node'

    A_DISPLAY_DIGITS_DEFAULT = 2
    A_DISPLAY_DIGITS_MAX = 10


    DEFAULT_CONFIGN_PATH = '/usr/local/LinuxNano/config/setup.xml'


    def enum(*enumerated):
        enums = dict(zip(enumerated, range(len(enumerated))))
        enums["names"] = enumerated
        return type('enum', (), enums)







    D_O_NAME_MAX_CHAR_LENGTH = 25

    MIN_HAL_PERIOD = 1000  # is this in nano seconds or what?
    MAX_HAL_PERIOD = 1000000000



    DEFAULT_SYSTEM_BACKGROUND  =  'linuxnano/resources/icons/general/generic_system_background.svg'
    DEFAULT_DEVICE_ICON        = 'linuxnano/resources/icons/general/unknown.svg'



    EDIT_TAB_ICON       = "/usr/local/LinuxNano/resources/menus/a_out_icon.png"
