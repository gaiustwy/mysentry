let canvas = document.getElementById('videoCanvas');

if (canvas) {
	let ctx = canvas.getContext('2d');
	let frame = document.getElementById('frame');
	let startX, startY, endX, endY;
	let drawing = false;
	let exclusionZones = [];

	// Function to set the canvas size to match the video frame size
	function setCanvasSize() {
		canvas.width = frame.clientWidth;
		canvas.height = frame.clientHeight;
	}

	// Set the canvas size when the frame is loaded and when the window is resized
	frame.onload = setCanvasSize;
	window.onresize = setCanvasSize;

	// Function to get the mouse position relative to the canvas
	function getMousePos(canvas, evt) {
		let rect = canvas.getBoundingClientRect();
		return {
			x: evt.clientX - rect.left,
			y: evt.clientY - rect.top
		};
	}

	// Start drawing on mousedown event
	canvas.addEventListener('mousedown', (e) => {
		let pos = getMousePos(canvas, e);
		startX = pos.x;
		startY = pos.y;
		drawing = true;
	});

	// Draw the exclusion zone rectangle as the mouse moves
	canvas.addEventListener('mousemove', (e) => {
		// Only draw if the mouse is down
		if (!drawing) return;
		let pos = getMousePos(canvas, e);
		endX = pos.x;
		endY = pos.y;
		ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear the canvas before redrawing
		ctx.fillStyle = 'rgba(255, 0, 0, 0.2)';	// Semi-transparent red for the exclusion zone
		ctx.fillRect(startX, startY, endX - startX, endY - startY);	// Draw the current rectangle

		// Redraw all existing exclusion zones
		exclusionZones.forEach(zone => {
			ctx.fillRect(zone.startX, zone.startY, zone.endX - zone.startX, zone.endY - zone.startY);
		});
	});

	// Finish drawing on mouseup event
	canvas.addEventListener('mouseup', () => {
		drawing = false; // Stop drawing
		// Save the drawn rectangle as an exclusion zone
		exclusionZones.push({ startX, startY, endX, endY });

		// Redraw all exclusion zones including the new one
		exclusionZones.forEach(zone => {
			ctx.fillRect(zone.startX, zone.startY, zone.endX - zone.startX, zone.endY - zone.startY);
		});

		// Send exclusion zones to the server
		fetch('/set_exclusion_zones', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ zones: exclusionZones })
		});
	});

	// Clear all exclusion zones and the canvas when the clear button is clicked
	document.getElementById('clearButton').addEventListener('click', () => {
		exclusionZones = []; // Clear the exclusion zones array
		ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear the canvas
		fetch('/clear_exclusion_zones', { // Inform the server to clear the exclusion zones
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			}
		});
	});

	// Toggle motion detection state without reloading the page
	document.getElementById('toggleMotionButton').addEventListener('click', () => {
	fetch('/toggle_motion_detection', {
		method: 'POST'
	}).then(response => response.json())
		.then(data => {
			let button = document.getElementById('toggleMotionButton');

			// Update the button state and text based on the current motion detection status
			if (data.motion_detection_active) {
				button.innerHTML = '<i class="bi bi-stop-circle"></i>&nbspStop Motion Detection';
				button.classList.remove('btn-outline-primary');
				button.classList.add('btn-outline-danger');
			} else {
				button.innerHTML = '<i class="bi bi-play-circle"></i>&nbspStart Motion Detection';
				button.classList.remove('btn-outline-danger');
				button.classList.add('btn-outline-primary');
			}
		});
	});
}