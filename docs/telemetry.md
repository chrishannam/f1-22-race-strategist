# Telemetry
[UDP packet explanation](https://forums.codemasters.com/topic/54423-f1%C2%AE-2020-udp-specification/) covers
the data sent from the F1 2021 game in great detail. Below is an overview gathered from that
page.

|  **Packet** | **Frequency**  | **Notes**  |
|:--- | :---: | ---: |
|Motion|User Defined|-|
|Session|2 Per Second|-|
|Lap|User Defined|-|
|Event|When Triggered|-|
|Participants| 1 Per 5 Seconds|-|
|Car Setup| 2 Per Second|-|
|Car Telemetry|User Defined|-|
|Car Status|User Defined|-|
|Final Classification| 1|Only at the end of the race|


## Events

|Event|Code|Description|
|:--- | :---: | ---: |
|Session Started|**SSTA**|Sent when the session starts|
|Session Ended|**SEND**|Sent when the session ends|
|Fastest Lap|**FTLP**|When a driver achieves the fastest lap
|Retirement|**RTMT**|When a driver retires|
|DRS enabled|**DRSE**|Race control have enabled DRS|
|DRS disabled|**DRSD**|Race control have disabled DRS|
|Team mate in pits|**TMPT**|Your team mate has entered the pits|
|Chequered flag|**CHQF**|The chequered flag has been waved|
|Race Winner|**RCWN**|The race winner is announced|
|Penalty Issued|**PENA**| A penalty has been issued – details in event|
|Speed Trap Triggered|**SPTP**|Speed trap has been triggered by fastest speed|


b'\xe5\x07\x01\x03\x01\x03I\x1b\x1a\x04RO^\x8fT\x10\xd3C\xffV\x00\x00\x13\xffBUTN\x04\x00\x00\x00\x03\x00\x00\x00'


Packet IDs
The packets IDs are as follows:

Packet Name

Value

Description

Motion

0

Contains all motion data for player’s car – only sent while player is in control

Session

1

Data about the session – track, time left

Lap Data

2

Data about all the lap times of cars in the session

Event

3

Various notable events that happen during a session

Participants

4

List of participants in the session, mostly relevant for multiplayer

Car Setups

5

Packet detailing car setups for cars in the race

Car Telemetry

6

Telemetry data for all cars

Car Status

7

Status data for all cars such as damage

Final Classification

8

Final classification confirmation at the end of a race

Lobby Info

9

Information about players in a multiplayer lobby