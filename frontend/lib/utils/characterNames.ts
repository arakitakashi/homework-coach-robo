import type { CharacterType } from "@/types"

/**
 * キャラクタータイプから表示名へのマッピング
 */
export const CHARACTER_NAMES: Record<CharacterType, string> = {
	robot: "ロボ",
	wizard: "まほうつかい",
	astronaut: "うちゅうひこうし",
	animal: "どうぶつ",
} as const

/**
 * キャラクタータイプから表示名を取得する
 *
 * @param character - キャラクタータイプ
 * @returns 表示名
 */
export function getCharacterName(character: CharacterType): string {
	return CHARACTER_NAMES[character]
}
