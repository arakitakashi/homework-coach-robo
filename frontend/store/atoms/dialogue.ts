/**
 * 対話状態管理のJotai atoms
 */

import { atom } from "jotai"
import type { CharacterState, DialogueTurn, HintLevel } from "@/types"

/** 対話履歴 */
export const dialogueTurnsAtom = atom<DialogueTurn[]>([])

/** 現在のヒントレベル */
export const hintLevelAtom = atom<HintLevel>(0)

/** キャラクター状態 */
export const characterStateAtom = atom<CharacterState>("idle")
