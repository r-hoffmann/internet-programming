from operator import attrgetter

from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub

# This is the learning switch you have already created
# Now you extend the learning switch with monitoring capability
from learning_switch import LearningSwitch13


# The switch monitor function extends the learning switch
class SwitchMonitor13(LearningSwitch13):

    def __init__(self, *args, **kwargs):
        super(SwitchMonitor13, self).__init__(*args, **kwargs)

        # Maintain a table for all the datapaths in the network
        self.datapaths = {}

        # Start a new thread for monitoring
        # The new thread excutes the function _monitor
        self.monitor_thread = hub.spawn(self._monitor)

    # Handle state change event
    # Register/Deregister a datapath
    @set_ev_cls(ofp_event.EventOFPStateChange,
                [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath

        # --------------------------------------------------------
        # Your code starts here
        # --------------------------------------------------------
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]

    # Request statistics information from all datapaths every 5s
    def _monitor(self):

        while True:
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(5)

    # Request statistics information from a datapath
    def _request_stats(self, datapath):
        self.logger.debug('send stats request: %016x', datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # --------------------------------------------------------
        # Your code starts here
        # --------------------------------------------------------
        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)

    # Handle flow stats information from the datapaht
    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):

        body = ev.msg.body
        dpid = ev.msg.datapath.id

        # --------------------------------------------------------
        # Your code starts here
        # Monitor the specified ports on two switches:
        # dpid=1 and dpid=2
        # --------------------------------------------------------
        self.logger.info('datapath         '
                         'in-port  eth-dst           '
                         'out-port packets  bytes')
        self.logger.info('---------------- '
                         '-------- ----------------- '
                         '-------- -------- --------')
        for stat in sorted([flow for flow in body if flow.priority == 1],
                           key=lambda flow: (flow.match['in_port'],
                                             flow.match['eth_dst'])):
            self.logger.info('%016x %8x %17s %8x %8d %8d',
                             ev.msg.datapath.id,
                             stat.match['in_port'], stat.match['eth_dst'],
                             stat.instructions[0].actions[0].port,
                             stat.packet_count, stat.byte_count)
