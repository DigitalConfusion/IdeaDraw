// Create a connection to SocketIO object
var socket = io();

// Variables
let player_place_id;
let ready_player_count = 1;

// Wait for window to load
window.onload = function () {
  // Connect to the socketIO room on the server side
  // Returns data about current session and stores to browsers storage
  socket.emit("connect_to_lobby", (session_data) => {
    // Save data to storage
    sessionStorage.setItem("lobby_code", session_data["lobby_code"]);
    sessionStorage.setItem("players", session_data["players"]);
    sessionStorage.setItem("player_id", session_data["player_id"]);
    sessionStorage.setItem("drawing_stage", 1);

    // Show correct lobby code
    document.getElementById("lobby_code").innerHTML =
      sessionStorage.getItem("lobby_code");
    update_lobby_players();

    // Add a listener to READY/NOT READY button
    // On click button changes the displayed name and the indicator changes colors
    document.getElementById("ready").addEventListener("click", function () {
      var button = document.getElementById("ready");
      if (button.innerHTML == "READY") {
        document.getElementById(
          "p" + player_place_id + "_indicator"
        ).style.backgroundColor = "limegreen";
        button.innerHTML = "NOT READY";
        socket.emit(
          "player_is_ready",
          parseInt(sessionStorage.getItem("player_id"))
        );
      } else if (button.innerHTML == "NOT READY") {
        document.getElementById(
          "p" + player_place_id + "_indicator"
        ).style.backgroundColor = "#ffe433";
        button.innerHTML = "READY";
        socket.emit(
          "player_not_ready",
          parseInt(sessionStorage.getItem("player_id"))
        );
      }
    });
  });
};

// Go through every player in the player list and update the username and
// the indicator in the lobby screen
async function update_lobby_players() {
  let place_id;
  let player_id = parseInt(sessionStorage.getItem("player_id"));

  players = JSON.parse(sessionStorage.getItem("players"));

  for (let [player, id] of Object.entries(players)) {
    if (id != null) {
      // Split key name to get lobby place player occupies
      // Example: player.split("") returns 1
      place_id = player.split("")[7];
      id = id.toString();

      // Compare id from player list, if it matches, we get the lobby place which the player occupies
      if (id == player_id) {
        player_place_id = place_id;
      }

      // If the player is the lobby leader, show the START button
      // otherwise only show the READY/NOT READY button
      if (place_id == "1" && id == player_id) {
        document.getElementById("start").hidden = false;
        document.getElementById("ready").hidden = true;
      } else if (place_id != "1" && id == player_id) {
        document.getElementById("ready").hidden = false;
      }

      // Request the username of the player with the specific ID
      await new Promise((resolve) => {
        socket.emit("get_username", id, (username) => {
          // Set the username of the player based on their place in the lobby
          document.getElementById("p" + place_id + "name").innerHTML = username;
          // Change the indicator color to green if the player is the lobby leader
          // else set it to red
          indicator = document.getElementById("p" + place_id + "_indicator");
          if (place_id == 1) {
            indicator.style.backgroundColor = "limegreen";
          } else {
            indicator.style.backgroundColor = "#ffe433";
          }
          resolve(username);
        });
      });
    }
  }
}

// If new player joins, update player list and displayed data
socket.on("player_joined", async function (players) {
  sessionStorage.setItem("players", players);
  update_lobby_players();
});

// Adds function to start button to check if atleast 3 players are in the lobby
// If there is start the game, otherwise show a warning
document.getElementById("start").addEventListener("click", async function () {
  await new Promise((resolve) => {
    socket.emit("get_player_count", (player_count) => {
      if (player_count >= 3) {
        if (ready_player_count == player_count) {
          socket.emit("begin_first_round");
        } else if (
          confirm(
            "Not all players have pressed READY! Do you want to continue start the game anyways?"
          )
        ) {
          socket.emit("begin_first_round");
        } else {
          alert("Wait for all players to press READY!");
        }
      } else {
        alert(
          "Not enough players! There needs to be at least 3 players in the lobby!"
        );
      }
      resolve(player_count);
    });
  });
});

// Redirect player to first round
socket.on("redirect_to_first_round", (url) => {
  window.location.href = url;
});

// If some player has pressed ready, change that players indicator color to green
socket.on("ready_player_id", (username) => {
  ready_player_count += 1;
  for (i = 2; i <= 8; i++) {
    if (
      document.getElementById("p" + i.toString() + "name").innerHTML == username
    ) {
      document.getElementById("p" + i + "_indicator").style.backgroundColor =
        "limegreen";
      break;
    }
  }
});

// If some player has pressed not ready, change that players indicator color to red
socket.on("not_ready_player_id", (username) => {
  ready_player_count -= 1;
  for (i = 2; i <= 8; i++) {
    if (
      document.getElementById("p" + i.toString() + "name").innerHTML == username
    ) {
      document.getElementById("p" + i + "_indicator").style.backgroundColor =
        "#ffe433";
      break;
    }
  }
});
