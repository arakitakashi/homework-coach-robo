/**
 * PCM Player Processor
 *
 * AudioWorkletProcessor that receives 16-bit PCM audio data from the main thread,
 * stores it in a ring buffer, and plays it back.
 *
 * Expected input: ArrayBuffer containing 16-bit signed integers (Int16Array)
 * Output sample rate: 24kHz (Gemini Live API output format)
 */
class PCMPlayerProcessor extends AudioWorkletProcessor {
	constructor() {
		super()

		// Ring buffer configuration
		// 24kHz * 180 seconds = enough for 3 minutes of audio
		this.bufferSize = 24000 * 180
		this.buffer = new Float32Array(this.bufferSize)
		this.writeIndex = 0
		this.readIndex = 0

		// Handle incoming messages from main thread
		this.port.onmessage = (event) => {
			// Handle control commands
			if (event.data && event.data.command === "endOfAudio") {
				// Clear the buffer by moving read index to write index
				this.readIndex = this.writeIndex
				return
			}

			// Decode the ArrayBuffer to Int16Array
			const int16Samples = new Int16Array(event.data)

			// Add the audio data to the ring buffer
			this._enqueue(int16Samples)
		}
	}

	/**
	 * Push incoming Int16 samples into the ring buffer.
	 * Converts 16-bit integers to float values in [-1, 1] range.
	 *
	 * @param {Int16Array} int16Samples - Audio samples as 16-bit integers
	 */
	_enqueue(int16Samples) {
		for (let i = 0; i < int16Samples.length; i++) {
			// Convert 16-bit integer to float in [-1, 1]
			// 32768 = 2^15 (max value for signed 16-bit)
			const floatVal = int16Samples[i] / 32768

			// Store in ring buffer (mono)
			this.buffer[this.writeIndex] = floatVal
			this.writeIndex = (this.writeIndex + 1) % this.bufferSize

			// Handle overflow by overwriting oldest samples
			if (this.writeIndex === this.readIndex) {
				this.readIndex = (this.readIndex + 1) % this.bufferSize
			}
		}
	}

	/**
	 * Process audio output.
	 * Called approximately every 128 samples (depending on browser).
	 * Reads from the ring buffer and writes to output channels.
	 *
	 * @param {Float32Array[][]} inputs - Audio input channels (unused)
	 * @param {Float32Array[][]} outputs - Audio output channels
	 * @param {Object} parameters - Audio parameters (unused)
	 * @returns {boolean} - Return true to keep the processor alive
	 */
	process(_inputs, outputs, _parameters) {
		const output = outputs[0]
		const framesPerBlock = output[0].length

		for (let frame = 0; frame < framesPerBlock; frame++) {
			// Read sample from buffer
			const sample = this.buffer[this.readIndex]

			// Write to left channel
			output[0][frame] = sample

			// Write to right channel if stereo output
			if (output.length > 1) {
				output[1][frame] = sample
			}

			// Move read index forward unless underflowing (buffer empty)
			if (this.readIndex !== this.writeIndex) {
				this.readIndex = (this.readIndex + 1) % this.bufferSize
			}
		}

		// Return true to keep the processor alive
		return true
	}
}

registerProcessor("pcm-player-processor", PCMPlayerProcessor)
