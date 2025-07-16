const socket = io('https://your-backend-server-url.com');
let roomId = '';
let boardSize = 30;
let cells = [];
let turn = 'X';
let mySymbol = null;
let lastMoveCell = null;

function createRoom() {
  socket.emit('create_room');
}

function joinRoom() {
  const inputRoomId = document.getElementById('room-id-input').value.trim();
  if (inputRoomId.length === 4) {
    roomId = inputRoomId;
    socket.emit('join_room', { room_id: roomId });
  }
}

socket.on('room_created', data => {
  roomId = data.room_id;
  alert(`បន្ទប់បានបង្កើត: ${roomId}`);
  document.getElementById('room-info').innerText = `Room ID: ${roomId}`;
  startGameUI();
});

socket.on('waiting_for_player', data => {
  alert(data.message);
});

socket.on('game_started', data => {
  if (data.room === roomId) {
    const playerIndex = data.players.indexOf(socket.id);
    mySymbol = playerIndex === 0 ? 'X' : 'O';
    turn = data.turn;
    document.getElementById('status').innerText = `វេនអ្នកលេង: ${turn}`;
    document.getElementById('room-info').innerText = `Room ID: ${roomId}`;
    startGameUI();
  }
});

socket.on('move_made', data => {
  const cell = cells[data.x][data.y];
  if (cell) {
    if (lastMoveCell) {
      lastMoveCell.classList.remove('last-move');
    }
    cell.textContent = data.symbol;
    cell.classList.add('clicked-cell');
    cell.classList.add('last-move');
    lastMoveCell = cell;
  }
  turn = data.symbol === 'X' ? 'O' : 'X';
  document.getElementById('status').innerText = `វេនអ្នកលេង: ${turn}`;
});

socket.on('game_over', data => {
  alert(`🏆 Player ${data.winner} ឈ្នះហើយ!`);
  lastMoveCell = null;
  createBoard(); // Reset UI board
  document.getElementById('room-info').innerText = `Room ID: ${roomId}`;
  turn = 'X';  // Reset turn for new game
});

socket.on('error', data => {
  alert(data.message || 'មានបញ្ហា!');
});

function startGameUI() {
  document.getElementById('lobby').style.display = 'none';
  document.getElementById('game-container').style.display = 'block';
  createBoard();
}

function createBoard() {
  const board = document.getElementById('board');
  board.innerHTML = '';
  board.style.display = 'grid';
  board.style.gridTemplateColumns = `repeat(${boardSize}, 30px)`;
  board.style.gridGap = '1px';

  cells = [];
  for (let i = 0; i < boardSize; i++) {
    cells[i] = [];
    for (let j = 0; j < boardSize; j++) {
      const cell = document.createElement('div');
      cell.className = 'cell';
      cell.dataset.x = i;
      cell.dataset.y = j;
      cell.onclick = () => {
        if (turn === mySymbol && cell.textContent === '') {
          makeMove(i, j);
        }
      };
      board.appendChild(cell);
      cells[i][j] = cell;
    }
  }
}

function makeMove(x, y) {
  socket.emit('make_move', { room: roomId, x, y });
}

// --- Register service worker for PWA support ---
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/static/sw.js')
      .then(registration => {
        console.log('Service Worker registered with scope:', registration.scope);
      })
      .catch(error => {
        console.log('Service Worker registration failed:', error);
      });
  });
}
