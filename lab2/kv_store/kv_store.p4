/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/
header kv_header_t {
    bit<64> preamble;
    bit<8> type;
    bit<32> key;
    bit<32> value;
}

struct metadata {

}

struct headers {
    kv_header_t             kv_header;
}

register<bit<32>>(1000) kv_store;

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {


    state start {
        transition parse_kv;
    }

    state parse_kv {
        packet.extract(hdr.kv_header);
        transition select(hdr.kv_header.preamble) {
            1: accept;
        }
    }
}


/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
    
    action reply() {
        bit<9> tmp;
        tmp = standard_metadata.ingress_port;
        standard_metadata.ingress_port = standard_metadata.egress_spec;
        standard_metadata.egress_spec = tmp;
    }

    apply {
        if (hdr.kv_header.type == 0) {
            kv_store.read(hdr.kv_header.value, hdr.kv_header.key);
            hdr.kv_header.type = 2;
            reply();
        } else if (hdr.kv_header.type == 1) {
            kv_store.write(hdr.kv_header.key, hdr.kv_header.value);
            hdr.kv_header.type = 3;
            reply();
        } 
     }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {  }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply { 
        packet.emit(hdr.kv_header);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/


V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
