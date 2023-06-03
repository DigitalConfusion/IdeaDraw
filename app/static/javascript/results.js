// Create a connection to SocketIO object
var socket = io();

// Join the SocketIO drawing room
socket.emit("join_results_room");

// On window loading compleation
window.onload = function () {
  // When play again button has been pressed,
  // redirect back to the home page
  document
    .getElementById("back_home_button")
    .addEventListener("click", function () {
      window.location.href = "/";
    });
  
  // Request the prompt of the lobby and update it on the page
  socket.emit("get_prompt", (prompt) => {
    document.getElementById("prompt").innerHTML = prompt;
  });

  // Request results from the server
  socket.emit("get_final_results", (results) => {
    // For each drawing in the list, update the page with the
    // drawings and their info
    for (const [key, value] of Object.entries(results)) {
      if (key == "first_drawing_image") {
        document.getElementById(key).src = value;
      } else if (key == "second_drawing_image") {
        document.getElementById(key).src = value;
      } else if (key == "third_drawing_image") {
        document.getElementById(key).src = value;
        document.getElementById("final_image").src = value;
      }
    }
  });
};
