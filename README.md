# IdeaDraw

Idea Draw is a fun multiplayer game, where players are challenged to come up with innovative solutions given a single
sentence. The game was created as a part of the competition "Ventspils ITC 2023" by team "YaSnoozeYaLoose".

## **Motivation**

The main challenge of "Ventspils ITC 2023" was coming up with a solution to a motivational problem. The objective of this
particular game is to motivate students and adults to come up with new ideas/solutions, as well as improve their creativity
and designing skills.

## **Build Status**

The game is currently still in development (some final patches are being made), therefore it contains some small issues.
Issues you might run into:

*Game might crash after refreshing the page

*Game might not work if attempting to login on multiple tabs

*Game might not work if another player leaves in the middle of the game

How to not run into these issues:

*PLEASE DO NOT REFRESH YOUR BROWSER WHILE PLAYING THE GAME

*PLEASE DO NOT LOG ON YOUR PROFILE ON MULTIPLE TABS IN THE SAME BROWSER

*PLEASE DO NOT LEAVE IN THE MIDDLE OF THE GAME

## **Features**

The game starts out with a single sentence, that contains an intriguing idea, that players have to quickly sketch. 
After the time is up, all players are able to vote for other sketches and the best one wins and goes to the next stage. 
In this stage, the winning painting is used as a template, and players are free to improve this sketch. After the time 
is up, players again vote for the best one, and it advances to the next stage. Now that the sketch has been finalized, 
players are able to colour it and do the finishing touches. Players vote for the last time and the final drawing has 
been decided.

## **Screenshots from the game**

![Create Lobby](https://github.com/DigitalConfusion/IdeaDrawV2/blob/master/screenshots/CreateLobby.png)
![Join Lobby](https://github.com/DigitalConfusion/IdeaDrawV2/blob/master/screenshots/JoinLobby.png)
![Draw](https://github.com/DigitalConfusion/IdeaDrawV2/blob/master/screenshots/Draw.png)

## **Tech/Framework used**

The game uses Python for back-end and HTML, CSS, JavaScript and Flask framework for front-end.

## **Code style**

The code is written in the standart code style.

## **Code examples**


```
socket.on("redirect", (url) => {
  window.location.href = url;
});
```
```
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
```
```
# This function initializes the database by executing the SQL schema script.
def init_db():
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))
```
## **Installation**

1. Check that you have Python 3.10.6 or later installed.
2. Download the repository.
3. Run the .bat file.
4. Open http://127.0.0.1:5000/ in your browser.

## **Tests**

The game has already been tested multiple times during the development process, to minimize the chances of un-seen 
bugs/mistakes.

## **Contribute**

This is a learning project, anyone can use it and improve it (fix bugs/improve features).

## **Credits**

The project has been created from scratch, using information available online and code snippets from the official
documentations.

## **License**

MIT Open souce license.
