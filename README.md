# Anonymizer
Anonymizer is a client-server application that anonymizes user-specified words from a text file using two reliable data transport protocols, TCP and UDP with stop-and-wait protocol.

## Challenges faced
In my program, the problem I faced while developing my application was my separate messages were appending when receving from the sender.
I managed to fix this problem by finishing up the UDP first. Then I’ve understood file transfer much better and implemented my approach of get/put functions in TCP.

