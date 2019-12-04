
class strings():



    TOOL_NODE = 'Tool_Node'
    SYSTEM_NODE = 'System_Node'
    DEVICE_NODE = 'Device_Node'

    DEVICE_ICON_NODE =  'Device_Icon_Node'

    IO_NODE = 'IO_Node'
    DIGITAL_INPUT_NODE  = 'Digital_Input_Node'
    DIGITAL_OUTPUT_NODE = 'Digital_Output_Node'

    ANALOG_INPUT_NODE  = 'Analog_Input_Node'
    ANALOG_OUTPUT_NODE = 'Analog_Output_Node'



    #Transition the 4 above to this style
    D_IN_NODE  = 'Digital_Input_Node'
    A_IN_NODE  = 'Analog_Input_Node'
    D_OUT_NODE = 'Digital_Output_Node'
    A_OUT_NODE = 'Analog_Output_Node'



    A_IN_DISPLAY_DIGITS_DEFAULT = 2
    A_IN_DISPLAY_DIGITS_MAX = 10

    A_OUT_DISPLAY_DIGITS_DEFAULT = 2
    A_OUT_DISPLAY_DIGITS_MAX = 10




    DEFAULT_CONFIGN_PATH = '/usr/local/LinuxNano/config/setup.xml'


    def enum(*enumerated):
        enums = dict(zip(enumerated, range(len(enumerated))))
        enums["names"] = enumerated
        return type('enum', (), enums)
        

    MANUAL_DISPLAY_TYPES = enum('buttons','combo_box')
    MANUAL_DISPLAY_BUTTONS = 'buttons'
    MANUAL_DISPLAY_COMBO_BOX = 'combo_box'


    ANALOG_MANUAL_DISPLAY_TYPES = enum('number_box','slider','dial')
    ANALOG_SCALE_TYPES = enum('linear','cubic_spline')



    D_O_NAME_MAX_CHAR_LENGTH = 25

    MIN_HAL_PERIOD = 1000  # is this in nano seconds or what?
    MAX_HAL_PERIOD = 1000000000



    DEFAULT_SYSTEM_BACKGROUND  =  "/usr/local/LinuxNano/resources/icons/unknown.svg"
    DEFAULT_DEVICE_ICON        = '/usr/local/LinuxNano/resources/icons/general/unknown.svg'


    TREE_ICON_TOOL_NODE      = "/usr/local/LinuxNano/resources/menus/system_icon.png"
    TREE_ICON_SYSTEM_NODE      = "/usr/local/LinuxNano/resources/menus/system_icon.png"
    TREE_ICON_DEVICE_NODE      = "/usr/local/LinuxNano/resources/menus/device_icon.png"
    TREE_ICON_DEVICE_ICON_NODE = "/usr/local/LinuxNano/resources/menus/device_icon_icon.png"
    TREE_ICON_D_IN_NODE        = "/usr/local/LinuxNano/resources/menus/d_in_icon.png"
    TREE_ICON_A_IN_NODE        = "/usr/local/LinuxNano/resources/menus/a_in_icon.png"
    TREE_ICON_D_OUT_NODE       = "/usr/local/LinuxNano/resources/menus/d_out_icon.png"
    TREE_ICON_A_OUT_NODE       = "/usr/local/LinuxNano/resources/menus/a_out_icon.png"




    EDIT_TAB_ICON       = "/usr/local/LinuxNano/resources/menus/a_out_icon.png"



