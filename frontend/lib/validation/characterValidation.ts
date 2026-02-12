import type { CharacterType } from "@/types"

/**
 * 有効なキャラクタータイプの配列
 */
export const VALID_CHARACTERS = ["robot", "wizard", "astronaut", "animal"] as const

/**
 * キャラクタータイプのバリデーション
 *
 * @param character - 検証するキャラクター文字列
 * @returns 有効なキャラクタータイプの場合true、それ以外はfalse
 */
export function isValidCharacter(character: string | undefined): character is CharacterType {
	if (!character) {
		return false
	}
	return VALID_CHARACTERS.includes(character as CharacterType)
}
