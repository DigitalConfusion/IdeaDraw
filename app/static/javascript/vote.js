// Create a connection to SocketIO object
var socket = io();

// Variables
let vote;
let index = 1;

// Range element from page
range = document.getElementById("range");

// On redirect SocketIO event, redirect to the received URL
socket.on("redirect", (url) => {
  window.location.href = url;
});

// When elements have loaded
document.addEventListener("DOMContentLoaded", () => {
  // Join the SocketIO drawing room
  // Receive the current drawing stage and save it to browsers data storage
  // so data persists between screens
  socket.emit("join_voting_room", (drawing_stage) => {
    sessionStorage.setItem("drawing_stage", drawing_stage);
  });
  // Load all the drawings which the player has to vote for
  loadImages();
});

// Send request to the server to get
// all the drawings which player has to vote for
function loadImages() {
  socket.emit(
    "get_drawings_for_voting",
    parseInt(sessionStorage.getItem("player_id")),
    (images) => {
      // Object to store the drawings place in the carousel
      ids = {};

      // Loop over each image entry and load it into the image carousel
      // Save the index into which the drawing was into
      for (const [key, value] of Object.entries(images)) {
        document.getElementById("drawing" + index.toString()).src = value;
        ids[index - 1] = key;
        index++;
      }
    }
  );
}

// When document has fully loaded
$(document).ready(function () {
  // Assign functions to the action of the carousel sliding to the next image
  $("#voting_carousel").on(
    "slide.bs.carousel",
    async function (carousel_index) {
      console.log("Slide should happen now");
      // Get the vote
      vote = parseFloat(range.value);
      // Submit vote to server
      socket.emit("submit_vote", ids[carousel_index.from], vote);

      // Change vote value back to default
      range.value = 5;
      document.getElementById("num").value = 5;

      // If carousel has reached the end
      if (index - 1 == carousel_index.to || carousel_index.to == 0) {
        console.log("Screen should be hidden");
        // Hide the voting screen
        document.getElementById("voting_stage").hidden = true;
        // Show spinner
        document.getElementById("wait_for_others").hidden = false;
        document.getElementById("wait_for_others_text").hidden = false;

        // Check if all player have voted
        await new Promise((resolve) => {
          socket.emit("check_if_all_players_have_voted", (redirect) => {
            console.log("check_if_all_players_have_voted");
            // Redirect to next round
            if (redirect) {
              socket.emit("redirect_to_next_round");
              resolve(redirect);
            }
          });
        });
      }
    }
  );
});
