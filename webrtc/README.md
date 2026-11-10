# Two-peer WebRTC data channel in C++

This small program connects two C++ clients and lets them exchange text over a
WebRTC data channel. It demonstrates offer/answer signaling, ICE candidate
gathering, peer connection state, and messages. It does not send audio or video.

WebRTC includes ICE, DTLS, SCTP, and (for media) SRTP. Implementing and securing
those protocols from scratch would obscure the concepts this codelab is meant
to show. The example uses [libdatachannel](https://github.com/paullouisageneau/libdatachannel)
for the WebRTC protocol stack. Signaling is deliberately manual: copy the SDP
between the two terminals. This avoids adding a signaling server, WebSocket
framework, or JSON library.

## Build

Requires Linux, CMake 3.21+, a C++17 compiler, Make, and OpenSSL development
files. The build fetches libdatachannel v0.24.6 and its required dependencies
from GitHub. It disables media, examples, tests, and WebSocket support; the
program only needs data channels.

```sh
make
```

## Connect two clients

Open two terminals. In terminal A, start the offerer:

```sh
./build/peer offer
```

In terminal B, start the answerer:

```sh
./build/peer answer
```

Copy the `BEGIN_SDP` through `END_SDP` block from A and paste it into B. B then
prints its answer SDP; copy that block back into A. When the data channel opens,
type messages in either terminal. Enter `/quit` to exit.

### Localhost

Run both clients on the same computer as above. No STUN or TURN server is
needed; ICE can use local host candidates.

### Local network

Run one client on each computer on the same LAN. Use the same offer/answer steps
and no extra arguments. The computers must be able to exchange UDP traffic;
host firewalls can block ICE.

### Over the internet

Use the same offer/answer process, but transfer the SDP blocks through a
signaling path both clients can reach. The SDP carries temporary ICE
credentials, so use a private channel. Configure a STUN server on both peers to
discover public-facing addresses:

```sh
./build/peer offer stun:stun.l.google.com:19302
./build/peer answer stun:stun.l.google.com:19302
```

Direct ICE may fail when a NAT or firewall blocks peer-to-peer UDP. In that
case, both clients need access to a TURN relay and credentials:

```sh
./build/peer offer stun:stun.l.google.com:19302 turn.example.net 3478 USER PASS
./build/peer answer stun:stun.l.google.com:19302 turn.example.net 3478 USER PASS
```

Replace these values with details from a TURN service. STUN/TURN servers help
peers find or relay network paths; they do not carry the signaling messages.
The Internet example therefore needs both an out-of-band way to exchange SDP
and network access to STUN, or TURN when direct connectivity fails.

## What happens

1. The offerer creates a data channel and an SDP offer.
2. Each peer gathers ICE candidates and includes them in its SDP block.
3. The peers exchange offer and answer; ICE checks candidate pairs.
4. DTLS establishes encryption, then SCTP carries data-channel messages.

This waits for ICE gathering to finish before printing SDP, which keeps the
signaling flow easy to follow. Production applications usually use an
authenticated signaling service and trickle ICE to exchange candidates as
they are discovered.

## Clean

```sh
make clean
```
