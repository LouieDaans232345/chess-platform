// Initialize variables for the game and board
let board = null;
let game = null;

// Function to initialize the game
function initializeGame() {
    console.log("Initializing game...");
    game = new Chess();
    
    // Chessboard configuration
    const config = {
        draggable: true,
        position: 'start',
        onDrop: onPieceDrop
    };

    board = Chessboard('board', config);
    updateStatus();
}

// Start a new game
function startNewGame() {
    game.reset();
    board.position('start');
    updateStatus();
}

// Reset the game
function resetGame() {
    game.reset();
    board.position('start');
    updateStatus();
}

// Undo the last move
function undoMove() {
    game.undo();
    board.position(game.fen());
    updateStatus();
}

// Handle piece drop on the board
function onPieceDrop(source, target) {
    const move = game.move({
        from: source,
        to: target,
        promotion: 'q' // Always promote to queen for simplicity
    });

    if (move === null) return 'snapback'; // Illegal move
    updateStatus();
}

// Update game status
function updateStatus() {
    let status = '';
    const moveColor = game.turn() === 'b' ? 'Black' : 'White';

    // Check for checkmate, draw, or ongoing game
    if (game.in_checkmate()) {
        status = 'Game over, ' + moveColor + ' is in checkmate.';
    } else if (game.in_draw()) {
        status = 'Game over, drawn position';
    } else {
        status = moveColor + ' to move';
        if (game.in_check()) {
            status += ', ' + moveColor + ' is in check';
        }
    }

    document.getElementById('status').innerText = status;
}

// Initialize the game when the page loads
window.onload = initializeGame;
