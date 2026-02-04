/**
 * セッション状態管理のJotai atoms
 */

import { atom } from "jotai";
import type {
  CharacterType,
  LearningProgress,
  Session,
  SessionStatus,
} from "@/types";

/** 現在のセッション */
export const sessionAtom = atom<Session | null>(null);

/** セッション状態 */
export const sessionStatusAtom = atom<SessionStatus>("idle");

/** 選択されたキャラクター */
export const selectedCharacterAtom = atom<CharacterType>("robot");

/** 学習進捗 */
export const learningProgressAtom = atom<LearningProgress>({
  selfDiscoveryCount: 0,
  hintDiscoveryCount: 0,
  togetherCount: 0,
});

/** 合計ポイント（派生atom） */
export const totalPointsAtom = atom((get) => {
  const progress = get(learningProgressAtom);
  return (
    progress.selfDiscoveryCount * 3 +
    progress.hintDiscoveryCount * 2 +
    progress.togetherCount * 1
  );
});
