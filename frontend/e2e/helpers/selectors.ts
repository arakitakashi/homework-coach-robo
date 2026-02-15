/**
 * E2Eテスト用セレクタ・テキスト定数
 *
 * UIに表示される日本語テキストを集約し、テスト間の一貫性を保つ。
 */

/** ホームページのテキスト */
export const HOME = {
	title: "宿題コーチロボット",
	subtitle: "いっしょに がんばろう！",
	characterPrompt: "キャラクターを選んでね",
	startButton: "はじめる",
	characters: {
		robot: "ロボット",
		wizard: "まほうつかい",
		astronaut: "うちゅうひこうし",
		animal: "どうぶつ",
	},
} as const

/** セッションページのテキスト */
export const SESSION = {
	loading: "じゅんびちゅう...",
	endButton: "おわる",
	welcomeMessage: "こんにちは！いっしょにがんばろうね！",
	emptyDialogue: "対話を始めよう！",
	textInputPlaceholder: "ここにかいてね",
	sendButton: "送る",
	inputAriaLabel: "メッセージ入力",
	sendAriaLabel: "送信",
	dialogueLogAriaLabel: "対話履歴",
	errorTitle: "エラー",
	dialogueErrorTitle: "そうしんエラー",
	retryButton: "もういちど",
	backButton: "もどる",
	closeButton: "とじる",
} as const

/** 入力モード選択のテキスト */
export const INPUT_MODE_SELECTOR = {
	title: "どうやってつたえる？",
	voiceButton: "声で伝える",
	imageButton: "写真で伝える",
} as const

/** 音声UIのテキスト */
export const VOICE = {
	idle: "話しかけてね",
	recording: "録音中...",
	playing: "聞いているよ",
	connecting: "接続中...",
	startRecordingLabel: "録音を開始",
	stopRecordingLabel: "録音を止める",
	disabledNote: "（おんせいにゅうりょくはじゅんびちゅう）",
} as const

/** APIエンドポイント */
export const API = {
	sessions: "**/api/v1/dialogue/sessions",
	sessionsCreate: "**/api/v1/dialogue/sessions",
	sessionById: "**/api/v1/dialogue/sessions/*",
	dialogueRun: "**/api/v1/dialogue/run",
	voiceStream: "**/ws/**",
} as const
