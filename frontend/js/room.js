/* =====================================================
   AUTH + ROOM
===================================================== */
const token = localStorage.getItem("token");
if (!token) window.location.href = "/static/index.html";

const params = new URLSearchParams(window.location.search);
const roomCode = params.get("code");
document.getElementById("room").innerText = roomCode;

const myId = JSON.parse(atob(token.split(".")[1])).sub;

/* =====================================================
   STATE
===================================================== */
let ws;

let players = [];
let currentTurn = null;

let myHand = [];
let selectedCards = [];

let pileCount = 0;
let lastPlayCount = 0;

let lastRevealedCards = [];

let isDoubtTransition = false; // lock variable for showing doubt cards
/* =====================================================
   WEBSOCKET
===================================================== */
function connect() {
  ws = new WebSocket(`ws://127.0.0.1:8000/ws/${roomCode}/${token}`);

  ws.onmessage = (e) => {
    const data = JSON.parse(e.data);

    switch (data.type) {
      case "chat":
        renderChat(data);
        break;

      case "room_update":
        handleRoomUpdate(data);
        break;

      case "game_state":
        handleGameState(data);
        break;

      case "your_hand":
        myHand = data.hand || [];
        renderHand();
        break;

      case "game_event":
        handleGameEvent(data);
        break;

      case "error":
        alert(data.message);
        break;
    }
  };
}

connect();

/* =====================================================
   ROOM / GAME STATE
===================================================== */
function handleRoomUpdate(data) {
  players = data.players || [];
  currentTurn = data.current_turn || null;

  document.getElementById("players").innerText =
    "Players: " +
    players.map((p) => `${p.name} (${p.cards ?? "?"})`).join(", ");

  renderTablePlayers();
}

// ==============
// ==============
// winner message
// ==============
// ==============

function getPlayerNameById(id) {
  const p = players.find((x) => x.id === id);
  return p ? p.name : id;
}

// function handleGameState(data) {
//   // only PUBLIC info — pile, turn, etc
//   currentTurn = data.current_turn ?? currentTurn;
//   renderTablePlayers();
// }

function handleGameState(data) {
  // turn
  currentTurn = data.current_turn ?? currentTurn;

  // CLAIM
  document.getElementById("claim").innerText = data.claim ? data.claim : "-";

  const prevPile = pileCount;
  pileCount = data.pile_count ?? pileCount;

  // FORCE visual reset on new game
  if (prevPile !== pileCount && pileCount === 0) {
    renderPile();
  }

  renderTablePlayers();
}

/* =====================================================
   TABLE PLAYERS
===================================================== */
function renderTablePlayers() {
  if (!players.length) return;

  const positions = ["bottom", "left", "top", "right"];
  const myIndex = players.findIndex((p) => p.id === myId);
  if (myIndex === -1) return;

  const ordered = [...players.slice(myIndex), ...players.slice(0, myIndex)];

  positions.forEach((pos) => {
    const el = document.getElementById(`player-${pos}`);
    if (el) el.innerHTML = "";
  });

  ordered.slice(0, 4).forEach((p, i) => {
    const el = document.getElementById(`player-${positions[i]}`);
    if (!el) return;

    el.dataset.player = p.id;
    el.classList.toggle("active", p.id === currentTurn);

    el.innerHTML = `
      <div class="name">${p.id === myId ? "You" : p.name}</div>
      <div class="cards"></div>
      <div class="status"></div>
    `;

    if (p.id !== myId && p.cards > 0) {
      const cardsDiv = el.querySelector(".cards");
      for (let j = 0; j < p.cards; j++) {
        const c = document.createElement("div");
        c.className = "card back";
        cardsDiv.appendChild(c);
      }
    }
  });
}

/* =====================================================
   HAND
===================================================== */
function renderHand() {
  const hand = document.getElementById("hand");
  hand.innerHTML = "";
  selectedCards = [];

  myHand.forEach((card) => {
    const el = document.createElement("div");
    el.className = "card";
    el.innerText = card;

    el.onclick = () => toggleCard(card, el);
    hand.appendChild(el);
  });
}

function toggleCard(card, el) {
  if (selectedCards.includes(card)) {
    selectedCards = selectedCards.filter((c) => c !== card);
    el.classList.remove("selected");
  } else {
    if (selectedCards.length >= 4) return;
    selectedCards.push(card);
    el.classList.add("selected");
  }
}

/* =====================================================
   CONTROLS
===================================================== */
function startGame() {
  ws.send(JSON.stringify({ type: "start_game" }));
}

function play() {
  if (!selectedCards.length) return alert("Select cards");

  const claim = document.getElementById("claimSelect").value || null;

  ws.send(
    JSON.stringify({
      type: "play",
      cards: selectedCards,
      claim,
    })
  );

  selectedCards = [];
}

function passTurn() {
  ws.send(JSON.stringify({ type: "pass" }));
}

function doubt() {
  ws.send(JSON.stringify({ type: "doubt" }));
}

/* =====================================================
   GAME EVENTS
===================================================== */
function handleGameEvent(data) {
  switch (data.event) {
    case "cards_played":
      lastPlayCount = data.count;
      pileCount += data.count;
      renderPile();
      showPlayerStatus(data.by, `played ${data.count}`);
      break;

    case "pass":
      showPlayerStatus(data.by, "passed");
      break;

    case "doubt_result":
      isDoubtTransition = true;
      lastRevealedCards = data.cards || [];
      showPlayerStatus(data.by, "DOUBT!");
      revealLastPlayed();
      setTimeout(() => {
        isDoubtTransition = false; // Unlock
        clearPile();
      }, 1500);
      break;

    case "pile_dumped":
      clearPile();
      break;

    // case "game_over":
    //   alert(`Winner: ${data.winner}`);
    //   break;

    case "game_over": {
      const winnerName = getPlayerNameById(data.winner);
      renderSystemMessage(`🏆 ${winnerName} won the game`);

      // HARD RESET TABLE STATE
      pileCount = 0;
      lastPlayCount = 0;
      lastRevealedCards = [];

      // CLEAR PILE DOM
      document.getElementById("pileCards").innerHTML = "";
      document.getElementById("lastPlayed").innerHTML = "";

      // CLEAR CLAIM
      document.getElementById("claim").innerText = "-";

      // CLEAR PLAYER STATUS TEXTS
      document
        .querySelectorAll(".table-player .status")
        .forEach((s) => (s.innerText = ""));

      break;
    }
  }
}

/* =====================================================
   PILE
===================================================== */
function renderPile() {
  if (isDoubtTransition) return; // Stop the back-cards from overwriting the reveal

  const pile = document.getElementById("pileCards");
  const last = document.getElementById("lastPlayed");

  pile.innerHTML = "";
  last.innerHTML = "";

  const old = pileCount - lastPlayCount;

  for (let i = 0; i < old; i++) {
    const c = document.createElement("div");
    c.className = "card back";
    pile.appendChild(c);
  }

  for (let i = 0; i < lastPlayCount; i++) {
    const c = document.createElement("div");
    c.className = "card back separated";
    last.appendChild(c);
  }
}

// function revealLastPlayed() {
//   const last = document.getElementById("lastPlayed");
//   last.innerHTML = "";

//   for (let i = 0; i < lastPlayCount; i++) {
//     const c = document.createElement("div");
//     c.className = "card";
//     c.innerText = "🂠";
//     last.appendChild(c);
//   }
// }

function revealLastPlayed() {
  const last = document.getElementById("lastPlayed");
  last.innerHTML = "";

  lastRevealedCards.forEach((card) => {
    const c = document.createElement("div");
    c.className = "card";
    c.innerText = card; // REAL CARD VALUE
    last.appendChild(c);
  });
}

function clearPile() {
  pileCount = 0;
  lastPlayCount = 0;
  lastRevealedCards = [];
  renderPile();
}

/* =====================================================
   STATUS
===================================================== */
function showPlayerStatus(playerId, text) {
  const el = document.querySelector(`[data-player="${playerId}"]`);
  if (!el) return;

  const status = el.querySelector(".status");
  status.innerText = text;

  //   setTimeout(() => (status.innerText = ""), 2000);
  clearTimeout(status._timeout);
  status._timeout = setTimeout(() => {
    status.innerText = "";
  }, 1500);
}

/* =====================================================
   CHAT
===================================================== */
function renderChat(data) {
  const chat = document.getElementById("chat");
  chat.innerHTML += `<div><b>${data.user}:</b> ${data.message}</div>`;
  chat.scrollTop = chat.scrollHeight;
}

function renderSystemMessage(text) {
  const chat = document.getElementById("chat");
  chat.innerHTML += `
    <div class="system-msg"><b>${text}</b></div>
  `;
  chat.scrollTop = chat.scrollHeight;
}

function send() {
  const msg = document.getElementById("msg").value.trim();
  if (!msg) return;

  ws.send(JSON.stringify({ type: "chat", message: msg }));
  document.getElementById("msg").value = "";
}

/* =====================================================
   LEAVE
===================================================== */
function leaveRoom() {
  if (ws) ws.close();
  window.location.href = "/static/lobby.html";
}
