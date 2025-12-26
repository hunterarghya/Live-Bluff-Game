# 🎴 Live Bluff Game with Real-Time Video & Chat

A high-concurrency, real-time **Multi-Page Application** featuring the classic **Bluff (Cheat)** card game. This project demonstrates state synchronization, P2P communication, and asynchronous backend architecture.

---

## 🚀 Core Features

### 🎮 Gameplay Engine

- **Distributed State Management:** Real-time synchronization of game turns, card claims, and player hands across 2–4 players using FastAPI WebSockets.
- **Game Logic:** Full implementation of Bluff mechanics including card claiming, doubt (challenge) systems with visual card reveals, and automated pile management.
- **Session Continuity:** JWT-authenticated room management with persistent table seating and active turn highlighting.

### 🎥 Real-Time Communication (WebRTC & WebSockets)

- **Peer-to-Peer Video Calling:** Integrated **WebRTC (Mesh Architecture)** for low-latency video conferencing during gameplay. Video data is transmitted directly between peers, bypassing the server to optimize performance.
- **Signaling Server:** Leveraged the existing WebSocket infrastructure as a signaling channel for SDP offers/answers and ICE candidate exchange.
- **Media Controls:** Independent camera/mic toggles and a dedicated "Join/Hang Up" lifecycle management.
- **Live Chat:** Concurrent room-based messaging system for player interaction and automated system event logs.

### 🛡️ Security & Scalability

- **Authentication:** Secure user registration and login with JWT-protected routes and Argon2 password hashing.
- **Multi-User Isolation:** MongoDB-backed data isolation ensuring that player hands and private room data remain secure.

---

## 🧠 Technical Stack

### Backend

- **Framework:** FastAPI (Python)
- **Communication:** WebSockets (Real-time events) & WebRTC (Signaling)
- **Database:** MongoDB (User data & Room state)
- **Security:** JWT Authentication, Argon2 Hashing
- **Concurrency:** Asynchronous event loop for handling simultaneous game actions

### Frontend

- **Languages:** Vanilla JavaScript (ES6+), HTML5, CSS3
- **APIs:** MediaDevices API (Camera/Mic access), RTCPeerConnection (WebRTC)
- **Architecture:** Multi-Page Application (MPA) for clean state separation between Lobby and Game Room

---

## 🛠️ System Architecture

1. **The Handshake:** WebSockets establish the initial connection and manage the game state.
2. **The Signaling:** When a video call starts, the server acts as a relay for WebRTC metadata.
3. **The Stream:** Once the handshake is complete, video and audio flow directly between browsers using STUN servers to bypass NAT/Firewalls.

---

## 👤 Author

**Arghya Malakar** 📧 [arghyaapply2016@gmail.com](mailto:arghyaapply2016@gmail.com)  
🌐 GitHub: [hunterarghya](https://github.com/hunterarghya)
