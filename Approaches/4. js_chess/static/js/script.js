// chess.js


// Make computer move
function make_move () {
    // make HTTP request to backend
    $.post('/make_move', {'fen': game.fen()}, function (data) {
        // load fen of PY gamestate into the current JS game state
        game.move(data.best_move, { sloppy: true })
        // update board position
        board.position(game.fen())
        updateStatus()
    })
}

// Make 2 computer moves
function make_2_move() {
    // make HTTP request to backend for white's move
    $.post('/make_move', {'fen': game.fen()}, function(data) {
        // load fen of PY gamestate into the current JS game state
        game.move(data.best_move, { sloppy: true });
        // update board position
        board.position(game.fen());
        updateStatus();

        // make HTTP request to backend for black's move
        $.post('/make_move', {'fen': game.fen()}, function(data) {
            // load fen of PY gamestate into the current JS game state
            game.move(data.best_move, { sloppy: true });
            // update board position
            board.position(game.fen());
            updateStatus();
        });
    });
}


// Handle new game button
$('#new_game').on('click', function () {
    game.reset() // reset board
    board.position('start') // set initial board position
    updateStatus()
})

// Handle make move button
$('#make_move').on('click', function () {
    make_2_move()
})

// Handle take back button
$('#take_back').on('click', function () {
    game.undo() // undo last move made by computer
    game.undo() // undo last move made by player
    board.position(game.fen()) // update board position
    updateStatus()
})

// Handle flip board button
$('#flip_board').on('click', function () {
    board.flip()
})

// GUI board & game state variables
var board = null
var game = new Chess()
var $status = $('#status')
var $fen = $('#fen')
var $pgn = $('#pgn')
var $topMoves = $('#top_moves')

// On picking up a piece
function onDragStart (source, piece, position, orientation) {
    // do not pick up pieces if the game is over
    if (game.game_over()) return false
    
    // only pick up pieces for the side to move
    if ((game.turn() === 'w' && piece.search(/^b/) !== -1) ||
        (game.turn() === 'b' && piece.search(/^w/) !== -1)) {
            return false
        }
}

// On dropping a piece
function onDrop (source, target) {
    // see if the move is legal
    var move = game.move({
        from: source,
        to: target,
        promotion: 'q' // NOTE: always promote to a queen for example simplicity
    })

    // illegal move
    if (move === null) return 'snapback'

    // make computer move
    make_move()

    updateStatus()
}


// Update the board position after the piece snap
// for castling, en passant, pawn promotion
function onSnapEnd () {
    board.position(game.fen())
}


// Update game status
function updateStatus () {
    var status = ''

    var moveColor = 'White'
    if (game.turn() === 'b') {
        moveColor = 'Black'
    }

    // checkmate?
    if (game.in_checkmate()) {
        status = 'Game over, ' + moveColor + ' is in checkmate.'
    }

    // draw?
    else if (game.in_draw()) {
        status = 'Game over, drawn position'
    }

    // game still on
    else {
        status = moveColor + ' to move'

        // check?
        if (game.in_check()) {
            status += ', ' + moveColor + ' is in check'
        }
    }

    // top moves
    // make HTTP request to backend
    $.post('/get_top_moves', {'fen': game.fen()}, function (data) {
        top_moves = data.top_moves
    })

    // update DOM elements
    $status.html(status)
    $fen.html(game.fen())
    $pgn.html(game.pgn())
    $topMoves.html(top_moves)
}


// Chess board configuration
var config = {
    draggable: true,
    position: 'start',
    onDragStart: onDragStart,
    onDrop: onDrop,
    onSnapEnd: onSnapEnd,
    pieceTheme: '/static/img/chesspieces/wikipedia/{piece}.png'
}

// Create chess board widget instance
board = Chessboard('chess_board', config)

updateStatus()