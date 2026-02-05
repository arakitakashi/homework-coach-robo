/**
 * PCM Recorder Processor
 *
 * AudioWorkletProcessor that captures audio from the microphone
 * and sends Float32Array samples to the main thread.
 *
 * The main thread is responsible for converting to 16-bit PCM
 * and sending to the server.
 */
class PCMRecorderProcessor extends AudioWorkletProcessor {
	/**
	 * Process audio input from the microphone.
	 * Called approximately every 128 samples (depending on browser).
	 *
	 * @param {Float32Array[][]} inputs - Audio input channels
	 * @param {Float32Array[][]} outputs - Audio output channels (unused)
	 * @param {Object} parameters - Audio parameters (unused)
	 * @returns {boolean} - Return true to keep the processor alive
	 */
	process(inputs, _outputs, _parameters) {
		// Check if we have input data
		if (inputs.length > 0 && inputs[0].length > 0) {
			// Use the first channel (mono)
			const inputChannel = inputs[0][0]
			// Copy the buffer to avoid issues with recycled memory
			const inputCopy = new Float32Array(inputChannel)
			// Send to main thread
			this.port.postMessage(inputCopy)
		}
		// Return true to keep the processor alive
		return true
	}
}

registerProcessor("pcm-recorder-processor", PCMRecorderProcessor)
