# Warshipping_POC
Proof of concept tool for the warshipping attack vector used by IBM
## Features
  * The system may be configured to target a specific access point featuring a set full or partial ssid
  * If there is no payload, the device will simply attack all access points sequentially to collect passwords
  * PASSIVE MODE
    * System will scan for access points in its local vicinity
    * Once detected, the system will passively collect handshakes over set intervals
    * The device will check if a full 4-part handshake is collected, else it will re-scan/combine scans to obtain all 4 parts
    * once a full handshake is collected, this will be passed back to a C2 server to brute force
    * The C2 server will pass back the password and the device will launch a pre-configured attack
  * ACTIVE MODE
    * System will scan for access points in its local vicinity
    * Once detected, the system will launch a deauth attack upon the connected device that is the most active
    * The system will attempt to capture the re-connect handshake 
    * if the handshake is captured, it will be broadcast to the C2, else the attack will be launched again
    * the C2 will brute force the handshake and pass back the password and the device would launch its pre-configured attack

 ## Settings
    * Reattack attempts
      * For active attacks the number of times the device will attack a given station using a Deauth attack
      * For passive attacks, the number of attempts to capture the full handshake on the given network
    
    
