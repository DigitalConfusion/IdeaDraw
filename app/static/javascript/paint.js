// Create a connection to SocketIO object
var socket = io();

// Variables for the drawing section
let canvas_height = 600;
let canvas_width = 1.414213 * canvas_height;

let paint, brush_size, alpha, click_x, click_y, prior_x, prior_y;
let paint_color = 0;
let eraser_toggled = false;

// For undo/redo
let state_index = -1;
const states = [];

// Imported image variable
let img;

// On redirect SocketIO event, redirect to the received URL
socket.on("redirect", (url) => {
  window.location.href = url;
});

// On window loading compleation
window.onload = function () {
  // Request the prompt of the lobby and update it on the page
  socket.emit("get_prompt", (prompt) => {
    document.getElementById("prompt").innerHTML = prompt;
  });

  // Set each button to it's appropriate variable state
  // Brush brush_size
  document
    .getElementById("small_brush_size")
    .addEventListener("click", function () {
      brush_size = 2;
    });
  document
    .getElementById("medium_brush_size")
    .addEventListener("click", function () {
      brush_size = 5;
    });
  document
    .getElementById("big_brush_size")
    .addEventListener("click", function () {
      brush_size = 30;
    });

  // Color alpha
  document.getElementById("light").addEventListener("click", function () {
    alpha = 1;
  });
  document.getElementById("medium").addEventListener("click", function () {
    alpha = 2;
  });
  document.getElementById("dark").addEventListener("click", function () {
    alpha = 255;
  });
  // Tools
  // Undo
  document.getElementById("undo").addEventListener("click", function () {
    undo();
  });
  // Redo
  document.getElementById("redo").addEventListener("click", function () {
    // Redo doesn't work for some reason, don't have a clue why
    // If you press y, redo works perfectly
    redo();
  });
  // Delete the changes made to the drawing
  document.getElementById("delete").addEventListener("click", function () {
    clear();
    image(img, 0, 0);
  });
  // erase
  document.getElementById("erase").addEventListener("click", function () {
    // Toggle the erase on/off
    if (eraser_toggled) {
      eraser_toggled = false;
      document.getElementById("erase").style.backgroundColor = "#7452ff";
      document.getElementById("erase").style.transition = "all 0.5s";
    } else {
      eraser_toggled = true;
      document.getElementById("erase").style.backgroundColor = "#8e73fb";
      document.getElementById("erase").style.transition = "all 0.5s";
    }
  });

  // On submit button press, remove drawing screen,
  // and submit the drawing to DB. When drawing is submitted
  // emit a request to redirect to vote screen, after checking
  // if all players have submitted their drawing.
  document
    .getElementById("submit")
    .addEventListener("click", async function () {
      await new Promise((resolve) => {
        // Hide drawing screen
        document.getElementById("sketch_area").style.display = "none";
        // Show spinner
        document.getElementById("wait_for_others").style.display = "flex";
        // Submit drawing
        socket.emit(
          "submit_drawing",
          parseInt(sessionStorage.getItem("player_id")),
          canvas.toDataURL()
        );
        // Check if all players have submitted their drawings
        socket.emit("check_submited_drawings", (redirect) => {
          if (redirect) {
            // Request redirect to vote
            socket.emit("redirect_to_vote");
          }
          resolve(redirect);
        });
      });
    });
};

// Create p5.js canva
async function setup() {
  // Set default brush_size and stroke weight
  brush_size = 5;
  alpha = 255;

  // Create canva
  var canva = createCanvas(canvas_width, canvas_height);
  canva.parent("canvas_holder");

  // Add function to mouse release action event
  canva.mouseReleased(function () {
    // If state has been undone, and now drawing something else
    // delete all of the states after the state where drawing now
    if (state_index < states.length - 1) {
      states.length = state_index + 1;
    }
    // If mouse hasn't moved since clicking it, don't record the state
    if (!(click_x == mouseX && click_y == mouseY)) {
      saveState();
    }
  });

  // Save coordinate when mouse is pressed
  canva.mousePressed(function () {
    click_x = mouseX;
    click_y = mouseY;
  });

  // Set Canva background to white
  background(color(255));

  // Join the SocketIO drawing room
  // Receive the current drawing stage and save it to browsers data storage
  // so data persists between screens
  socket.emit("join_drawing_room", async (drawing_stage) => {
    sessionStorage.setItem("drawing_stage", drawing_stage);
    // Import the drawing that won the second stage
    await new Promise((resolve) => {
      socket.emit("get_drawing_for_next_round", (drawing) => {
        img = loadImage(drawing, () => {
          img.resize(canvas_width, canvas_height);
          image(img, 0, 0);
        });
        resolve(img);
      });
    });
  });

  // Create the color picker
  color_picker = createColorPicker("red");
  color_picker.parent("color_picker_holder");
  color_picker.style("width", "8vw");
  color_picker.style("height", "8vh");

  // Get the selected color from the color picker
  paint = color_picker.color();

  // Set framerate
  frameRate(60);
  // Stroke join option
  strokeJoin(ROUND);
}

// Runs continously at frame rate
function draw() {
  //store prior_x and Y for line drawing
  prior_x = mouseX;
  prior_y = mouseY;
}

// If mouse is dragged draw a line
function mouseDragged() {
  // If erase is on, change the brush to white
  // otherwise use the color selected
  if (eraser_toggled) {
    paint = color(255);
  } else {
    paint = color_picker.color();
  }

  // Set brush options
  paint.setAlpha(alpha);
  color(paint);
  stroke(paint);
  strokeWeight(brush_size);

  // Get mouse coordinates and add middle points
  // for them, to smoothen the drawn line
  m_x = mouseX;
  m_y = mouseY;
  mid_x = (prior_x + mouseX) / 2;
  mid_y = (prior_y + mouseY) / 2;
  mid1_x = (prior_x + mid_x) / 2;
  mid1_y = (prior_y + mid_y) / 2;
  mid2_x = (mid_x + m_x) / 2;
  mid2_y = (mid_y + m_y) / 2;

  line(prior_x, prior_y, mid1_x, mid1_y);
  line(mid1_x, mid1_y, mid_x, mid_y);
  line(mid_x, mid_y, mid2_x, mid2_y);
  line(mid2_x, mid2_y, m_x, m_y);
}

// Save current canva state
function saveState() {
  // Append state to array
  states.push(get());
  state_index += 1;
}

// When key pressed do Undo or Redo
function keyPressed(e) {
  // Undo (z)
  if (e.keyCode == 90) {
    undo();
  }
  // Redo (y)
  if (e.keyCode == 89) {
    redo();
  }
}

// Undo function
function undo() {
  // If no states saved, do nothing
  if (states.length == 0) {
    return;
  }

  // If undo past first saved state, show blank canva
  if (state_index < 0) {
    //background(color(255))
    //image(img, 0, 0, canvas_width, canvas_height)
    return;
  }

  // Index deincrement, because of undo
  state_index -= 1;

  // Set canva to blank
  background(color(255));
  image(img, 0, 0);

  // Load saved state using index
  if (state_index >= 0) {
    image(states[state_index], 0, 0);
  }
}

// Redo function
function redo() {
  // If no states saved, do nothing
  if (states.length == 0) {
    return;
  }
  // Increment index to go to next saved state
  state_index += 1;
  // If index is last in saved states, do nothing
  if (state_index > states.length - 1) {
    state_index -= 1;
    return;
  }
  // Set canva to blank
  background(color(255));
  image(img, 0, 0);
  // Load saved state using index
  image(states[state_index], 0, 0);
}
