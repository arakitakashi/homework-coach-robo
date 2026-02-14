/**
 * カメラ・画像認識の Jotai atoms
 *
 * CameraInterfaceの状態をグローバルに共有するためのatoms。
 * SessionContentが認識結果を読み取り、問題文としてセッション作成に使用する。
 */

import { atom } from "jotai"
import type { CameraStatus, ImageRecognitionResponse } from "@/types"

/** 入力モード: セッション開始時の選択（voice | image | null） */
export const inputModeAtom = atom<"voice" | "image" | null>(null)

/** カメラの現在の状態 */
export const cameraStatusAtom = atom<CameraStatus>("initial")

/** 画像認識結果（SessionContentが読み取る） */
export const cameraRecognitionAtom = atom<ImageRecognitionResponse | null>(null)

/** キャプチャした画像のBase64データ */
export const capturedImageAtom = atom<string | null>(null)
