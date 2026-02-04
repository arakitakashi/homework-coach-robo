/**
 * 音声関連の型定義
 */

/** 録音状態 */
export type RecordingState = "idle" | "recording" | "processing"

/** 音声設定 */
export interface AudioConfig {
	sampleRate: number
	channelCount: number
	echoCancellation: boolean
	noiseSuppression: boolean
}

/** デフォルト音声設定 */
export const DEFAULT_AUDIO_CONFIG: AudioConfig = {
	sampleRate: 16000,
	channelCount: 1,
	echoCancellation: true,
	noiseSuppression: true,
}
