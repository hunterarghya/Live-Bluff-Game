// const API = "http://127.0.0.1:8000";
// const token = localStorage.getItem("token");

// if (!token) {
//   window.location.href = "/static/index.html";
// }

// async function createRoom() {
//   const res = await fetch(`${API}/rooms/create`, {
//     method: "POST",
//     headers: {
//       Authorization: `Bearer ${token}`,
//     },
//   });

//   const data = await res.json();
//   if (res.ok) {
//     window.location.href = `/static/room.html?code=${data.room_code}`;
//   } else {
//     document.getElementById("msg").innerText = data.detail;
//   }
// }

// async function joinRoom() {
//   const code = document.getElementById("roomCode").value;

//   const res = await fetch(`${API}/rooms/join/${code}`, {
//     headers: {
//       Authorization: `Bearer ${token}`,
//     },
//   });

//   const data = await res.json();
//   if (res.ok) {
//     window.location.href = `/static/room.html?code=${code}`;
//   } else {
//     document.getElementById("msg").innerText = data.detail;
//   }
// }

// function logout() {
//   localStorage.removeItem("token");
//   localStorage.removeItem("name");
//   window.location.href = "/static/index.html";
// }

const API = "http://127.0.0.1:8000";

function getToken() {
  return localStorage.getItem("token");
}

/* Redirect if logged out */
if (!getToken()) {
  window.location.href = "/static/index.html";
}

/* ===== CREATE ROOM ===== */
async function createRoom() {
  const token = getToken();
  if (!token) {
    window.location.href = "/static/index.html";
    return;
  }

  const res = await fetch(`${API}/rooms/create`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  const data = await res.json();
  if (res.ok) {
    window.location.href = `/static/room.html?code=${data.room_code}`;
  } else {
    document.getElementById("msg").innerText = data.detail;
  }
}

/* ===== JOIN ROOM ===== */
async function joinRoom() {
  const token = getToken();
  if (!token) {
    window.location.href = "/static/index.html";
    return;
  }

  const code = document.getElementById("roomCode").value;

  const res = await fetch(`${API}/rooms/join/${code}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  const data = await res.json();
  if (res.ok) {
    window.location.href = `/static/room.html?code=${code}`;
  } else {
    document.getElementById("msg").innerText = data.detail;
  }
}

/* ===== LOGOUT ===== */
function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("name");
  window.location.href = "/static/index.html";
}
