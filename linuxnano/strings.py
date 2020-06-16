
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



    DEFAULT_SYSTEM_BACKGROUND  =  "/usr/local/LinuxNano/resources/icons/unknown.svg"
    DEFAULT_DEVICE_ICON        = '/usr/local/LinuxNano/resources/icons/general/unknown.svg'



    EDIT_TAB_ICON       = "/usr/local/LinuxNano/resources/menus/a_out_icon.png"
