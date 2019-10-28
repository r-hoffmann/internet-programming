                                                                                           
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel


'''
Run: 
    sudo python custom_topology.py

Om het netwerk te removen van mininet:
    sudo mn -c
'''
class multiSwitchTopo(Topo):
    "Multiple switches (n_switches) connected to multiple hosts (n_hosts) \
        with eavenly devided number of hosts per switch (hostsperswitch)."
    def __init__(self, n_switches=2, n_hosts=4, hostsperswitch=2):

        Topo.__init__( self )
        for i in range(n_switches):
            switch = self.addSwitch('s%s' % (i + 1))
            for j in range(n_hosts/hostsperswitch):
                host = self.addHost('h%s' % (i*hostsperswitch+j+1))
                print(switch, host)
                self.addLink(switch, host)
        self.addLink('s1','s2')


def simpleTest():
    "Create and test a simple network"
    topo = multiSwitchTopo(n_switches=2, n_hosts=4, hostsperswitch=2)
    net = Mininet(topo)
    net.start()
    print "Dumping host connections"
    dumpNodeConnections(net.hosts)
    print "Testing network connectivity"
    net.pingAll()
    net.stop()


if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    simpleTest()