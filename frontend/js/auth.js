// const API = "http://127.0.0.1:8000";

// async function login() {
//   const email = document.getElementById("email").value.trim();
//   const password = document.getElementById("password").value.trim();

//   if (!email || !password) {
//     document.getElementById("msg").innerText =
//       "Email and password are required";
//     return;
//   }

//   const res = await fetch(`${API}/auth/login`, {
//     method: "POST",
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify({ email, password }),
//   });

//   const data = await res.json();

//   if (res.ok) {
//     localStorage.setItem("token", data.access_token);
//     localStorage.setItem("name", data.name);
//     window.location.href = "/static/lobby.html";
//   } else {
//     document.getElementById("msg").innerText = data.detail;
//   }
// }

// async function register() {
//   const email = document.getElementById("email").value.trim();
//   const password = document.getElementById("password").value.trim();
//   const name = document.getElementById("name").value.trim();

//   if (!email || !password || !name) {
//     document.getElementById("msg").innerText =
//       "Email, password and name are required";
//     return;
//   }

//   const res = await fetch(`${API}/auth/register`, {
//     method: "POST",
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify({ email, password, name }),
//   });

//   const data = await res.json();

//   if (res.ok) {
//     localStorage.setItem("token", data.access_token);
//     localStorage.setItem("name", data.name);
//     window.location.href = "/static/lobby.html";
//   } else {
//     document.getElementById("msg").innerText = data.detail;
//   }
// }

// const API = "http://127.0.0.1:8000";
const API = window.location.origin;

/* ===== LOGIN ===== */
async function login() {
  const email = document.getElementById("login-email").value.trim();
  const password = document.getElementById("login-password").value.trim();

  if (!email || !password) {
    document.getElementById("msg").innerText =
      "Email and password are required";
    return;
  }

  const form = new URLSearchParams();
  form.append("username", email); // OAuth2 expects "username"
  form.append("password", password);

  const res = await fetch(`${API}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: form.toString(),
  });

  const data = await res.json();

  if (res.ok) {
    localStorage.setItem("token", data.access_token);
    localStorage.setItem("name", data.name);
    window.location.href = "/static/lobby.html";
  } else {
    document.getElementById("msg").innerText = data.detail;
  }
}

/* ===== REGISTER ===== */
async function register() {
  const email = document.getElementById("reg-email").value.trim();
  const password = document.getElementById("reg-password").value.trim();
  const name = document.getElementById("reg-name").value.trim();

  if (!email || !password || !name) {
    document.getElementById("msg").innerText =
      "Email, password and name are required";
    return;
  }

  const res = await fetch(`${API}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, name }),
  });

  const data = await res.json();

  if (res.ok) {
    localStorage.setItem("token", data.access_token);
    localStorage.setItem("name", data.name);
    window.location.href = "/static/lobby.html";
  } else {
    document.getElementById("msg").innerText = data.detail;
  }
}
