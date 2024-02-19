# =====================================================================
#  msgServer
# =====================================================================
class msgServer:
    def __init__(self, algName='',debugLevel=4):
        self.algName = algName
        self.text = ''

        # output debug level: DEBUG=0, INFO=1, WARNING=2, ERROR=3, FATAL=4
        self.debugLevel = debugLevel
        
        # Reset
        self.EndColor='\033[0m'       # Text Reset
        
        # Regular Colors
        self.Black='\033[0;30m'        # Black
        self.Red='\033[0;31m'          # Red
        self.Green='\033[0;32m'        # Green
        self.Yellow='\033[0;33m'       # Yellow
        self.Blue='\033[0;34m'         # Blue
        self.Purple='\033[0;35m'       # Purple
        self.Cyan='\033[0;36m'         # Cyan
        self.White='\033[0;37m'        # White

        # Bold
        self.BBlack='\033[1;30m'       # Black
        self.BRed='\033[1;31m'         # Red
        self.BGreen='\033[1;32m'       # Green
        self.BYellow='\033[1;33m'      # Yellow
        self.BBlue='\033[1;34m'        # Blue
        self.BPurple='\033[1;35m'      # Purple
        self.BCyan='\033[1;36m'        # Cyan
        self.BWhite='\033[1;37m'       # White

        # Underline
        self.UBlack='\033[4;30m'       # Black
        self.URed='\033[4;31m'         # Red
        self.UGreen='\033[4;32m'       # Green
        self.UYellow='\033[4;33m'      # Yellow
        self.UBlue='\033[4;34m'        # Blue
        self.UPurple='\033[4;35m'      # Purple
        self.UCyan='\033[4;36m'        # Cyan
        self.UWhite='\033[4;37m'       # White
        
        # Background
        self.On_Black='\033[40m'       # Black
        self.On_Red='\033[41m'         # Red
        self.On_Green='\033[42m'       # Green
        self.On_Yellow='\033[43m'      # Yellow
        self.On_Blue='\033[44m'        # Blue
        self.On_Purple='\033[45m'      # Purple
        self.On_Cyan='\033[46m'        # Cyan
        self.On_White='\033[47m'       # White

        # High Intensity
        self.IBlack='\033[0;90m'       # Black
        self.IRed='\033[0;91m'         # Red
        self.IGreen='\033[0;92m'       # Green
        self.IYellow='\033[0;93m'      # Yellow
        self.IBlue='\033[0;94m'        # Blue
        self.IPurple='\033[0;95m'      # Purple
        self.ICyan='\033[0;96m'        # Cyan
        self.IWhite='\033[0;97m'       # White

        # Bold High Intensity
        self.BIBlack='\033[1;90m'      # Black
        self.BIRed='\033[1;91m'        # Red
        self.BIGreen='\033[1;92m'      # Green
        self.BIYellow='\033[1;93m'     # Yellow
        self.BIBlue='\033[1;94m'       # Blue
        self.BIPurple='\033[1;95m'     # Purple
        self.BICyan='\033[1;96m'       # Cyan
        self.BIWhite='\033[1;97m'      # White

        # High Intensity backgrounds
        self.On_IBlack='\033[0;100m'   # Black
        self.On_IRed='\033[0;101m'     # Red
        self.On_IGreen='\033[0;102m'   # Green
        self.On_IYellow='\033[0;103m'  # Yellow
        self.On_IBlue='\033[0;104m'    # Blue
        self.On_IPurple='\033[0;105m'  # Purple
        self.On_ICyan='\033[0;106m'    # Cyan
        self.On_IWhite='\033[0;107m'   # White

        self.BLUE = '\033[94m'
        self.GREEN = '\033[92m'
        self.BOLD = "\033[1m"
        self.WARNING = '\033[93m'
        self.WARNING2 = '\033[95m'
        self.ERROR = '\033[91m'

        # define colors
        self.BLUE = '\033[94m'
        self.GREEN = '\033[92m'
        self.BOLD = "\033[1m"
        self.WARNING = '\033[93m'
        self.ERROR = '\033[91m'
        self.ENDC = '\033[0m'

        self.printDebug("MsgServer for %s is loaded successfully!" % algName)

    # =================================================================================
    #  print methods
    # =================================================================================
    def printDebug(self, msg):
        if self.debugLevel < 1: print '%-16s %-12s %s' % (self.algName, 'DEBUG', msg)
    def printInfo(self, msg):
        if self.debugLevel < 2: print '%-16s %-12s %s' % (self.algName, 'INFO', msg)
    def printWarning(self, msg):
        if self.debugLevel < 3: print self.Yellow + '%-16s %-12s %s' % (self.algName, 'WARNING', msg) + self.EndColor
    def printError(self, msg):
        if self.debugLevel < 4: print self.Red + '%-16s %-12s %s' % (self.algName, 'ERROR', msg) + self.EndColor
    def printFatal(self, msg):
        print self.BRed + '%-16s %-12s %s' % (self.algName, 'FATAL', msg) + self.EndColor

    # colors
    def printBlue(self, msg): print self.Blue + '%-16s %-12s %s' % (self.algName, 'INFO', msg) + self.EndColor
    def printRed(self, msg): print self.Red + '%-16s %-12s %s' % (self.algName, 'INFO', msg) + self.EndColor
    def printGreen(self, msg): print self.Green + '%-16s %-12s %s' % (self.algName, 'INFO', msg) + self.EndColor

    # extras
    def printBold(self, msg): print self.BOLD + '%-16s %-12s %s' % (self.algName, 'INFO', msg) + self.EndColor
