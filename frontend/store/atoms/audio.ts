/**
 * 音声状態管理のJotai atoms
 */

import { atom } from "jotai"
import type { RecordingState } from "@/types"

/** 録音状態 */
export const recordingStateAtom = atom<RecordingState>("idle")

/** 音声再生中フラグ */
export const isPlayingAtom = atom<boolean>(false)

/** 音声レベル（0-1の範囲） */
export const audioLevelAtom = atom<number>(0)
