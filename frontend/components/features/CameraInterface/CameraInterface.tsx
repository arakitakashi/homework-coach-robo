/**
 * CameraInterface コンポーネント
 *
 * 宿題プリントの画像をカメラ撮影またはファイルアップロードで取得し、
 * バックエンドの画像認識APIで問題文を抽出するUIコンポーネント。
 *
 * 6状態: initial → active → preview → processing → recognized / error
 * ターゲットユーザーは小学校低学年のため、大きなボタン・やさしい日本語で構成。
 */

"use client"

import type { ImageAnalysisResult } from "@/types"
import { useCameraCapture } from "./useCameraCapture"

/** CameraInterface のprops */
interface CameraInterfaceProps {
	/** 問題文認識完了時のコールバック */
	onProblemRecognized?: (recognizedText: string, result: ImageAnalysisResult) => void
}

/**
 * カメラインターフェースコンポーネント
 *
 * カメラ撮影またはファイルアップロードで宿題プリントの画像を取得し、
 * 画像認識APIで問題文を抽出する。
 */
export function CameraInterface({ onProblemRecognized }: CameraInterfaceProps) {
	const {
		status,
		error,
		capturedImage,
		recognitionResult,
		startCamera,
		captureImage,
		retake,
		recognizeImage,
		reset,
		handleFileUpload,
		videoRef,
	} = useCameraCapture()

	/** ファイル選択ハンドラ */
	const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
		const file = e.target.files?.[0]
		if (file) {
			handleFileUpload(file)
		}
	}

	/** 問題文確定ハンドラ */
	const onConfirmProblem = () => {
		if (recognitionResult && recognitionResult.problems.length > 0 && onProblemRecognized) {
			const firstProblem = recognitionResult.problems[0]
			onProblemRecognized(firstProblem.text, {
				recognizedText: firstProblem.text,
				problemType: firstProblem.type,
				confidence: recognitionResult.confidence,
				extractedExpression: firstProblem.expression,
			})
		}
	}

	return (
		<div className="flex flex-col items-center gap-4 p-4">
			{/* initial 状態: カメラ起動 or ファイルアップロード */}
			{status === "initial" && (
				<div className="flex flex-col items-center gap-4">
					<p className="text-lg font-bold text-gray-700">しゅくだいのしゃしんをとろう！</p>

					<button
						type="button"
						aria-label="カメラをつかう"
						className="min-h-[56px] min-w-[200px] rounded-2xl bg-blue-500 px-6 py-4 text-xl font-bold text-white shadow-lg hover:bg-blue-600 active:bg-blue-700"
						onClick={startCamera}
					>
						カメラをつかう
					</button>

					<div className="flex flex-col items-center gap-2">
						<label
							htmlFor="file-upload"
							className="cursor-pointer rounded-2xl border-2 border-dashed border-gray-300 px-6 py-4 text-lg text-gray-600 hover:border-blue-400 hover:text-blue-500"
						>
							しゃしんをえらぶ
							<input
								id="file-upload"
								type="file"
								accept="image/*"
								className="hidden"
								onChange={onFileChange}
							/>
						</label>
					</div>
				</div>
			)}

			{/* active 状態: ビデオプレビュー + 撮影ボタン */}
			{status === "active" && (
				<div className="flex flex-col items-center gap-4">
					{/* biome-ignore lint/a11y/useMediaCaption: カメラプレビューにキャプションは不要 */}
					<video
						ref={videoRef}
						autoPlay
						playsInline
						className="max-h-[400px] w-full max-w-[500px] rounded-xl bg-black"
					/>

					<button
						type="button"
						aria-label="しゃしんをとる"
						className="min-h-[64px] min-w-[64px] rounded-full bg-red-500 p-4 text-xl font-bold text-white shadow-lg hover:bg-red-600 active:bg-red-700"
						onClick={captureImage}
					>
						しゃしんをとる
					</button>
				</div>
			)}

			{/* preview 状態: キャプチャした画像 + 操作ボタン */}
			{status === "preview" && capturedImage && (
				<div className="flex flex-col items-center gap-4">
					<img
						src={capturedImage}
						alt="さつえいしたしゃしん"
						className="max-h-[400px] w-full max-w-[500px] rounded-xl"
					/>

					<div className="flex gap-4">
						<button
							type="button"
							aria-label="とりなおす"
							className="min-h-[48px] rounded-2xl bg-gray-400 px-6 py-3 text-lg font-bold text-white shadow hover:bg-gray-500"
							onClick={retake}
						>
							とりなおす
						</button>

						<button
							type="button"
							aria-label="もんだいをよみとる"
							className="min-h-[48px] rounded-2xl bg-green-500 px-6 py-3 text-lg font-bold text-white shadow-lg hover:bg-green-600"
							onClick={recognizeImage}
						>
							もんだいをよみとる
						</button>
					</div>
				</div>
			)}

			{/* processing 状態: 読み取り中 */}
			{status === "processing" && (
				<div className="flex flex-col items-center gap-4">
					{/* biome-ignore lint/a11y/useSemanticElements: outputは計算結果用で不適切。読み込みステータス表示 */}
					<div
						role="status"
						aria-label="よみとりちゅう"
						className="flex flex-col items-center gap-3"
					>
						<div className="h-12 w-12 animate-spin rounded-full border-4 border-blue-200 border-t-blue-500" />
						<p className="text-lg font-bold text-blue-600">よみとりちゅう...</p>
						<p className="text-gray-500">すこしまってね</p>
					</div>
				</div>
			)}

			{/* recognized 状態: 認識結果表示 */}
			{status === "recognized" && recognitionResult && recognitionResult.problems.length > 0 && (
				<div className="flex flex-col items-center gap-4">
					<div className="w-full max-w-[500px] rounded-xl bg-green-50 p-4">
						<p className="mb-2 text-sm font-bold text-green-700">よみとったもんだい:</p>
						<p className="text-xl font-bold text-gray-800">{recognitionResult.problems[0].text}</p>
					</div>

					<div className="flex gap-4">
						<button
							type="button"
							aria-label="とりなおす"
							className="min-h-[48px] rounded-2xl bg-gray-400 px-6 py-3 text-lg font-bold text-white shadow hover:bg-gray-500"
							onClick={retake}
						>
							とりなおす
						</button>

						<button
							type="button"
							aria-label="このもんだいでべんきょうする"
							className="min-h-[48px] rounded-2xl bg-green-500 px-6 py-3 text-lg font-bold text-white shadow-lg hover:bg-green-600"
							onClick={onConfirmProblem}
						>
							このもんだいでべんきょうする
						</button>
					</div>
				</div>
			)}

			{/* error 状態: エラーメッセージ + フォールバック */}
			{status === "error" && (
				<div className="flex flex-col items-center gap-4">
					{/* biome-ignore lint/a11y/useSemanticElements: outputは計算結果用で不適切。エラーステータス表示 */}
					<div role="alert" className="w-full max-w-[500px] rounded-xl bg-red-50 p-4">
						<p className="text-lg font-bold text-red-600">{error?.message}</p>
					</div>

					<div className="flex flex-col items-center gap-3">
						<label
							htmlFor="file-upload-fallback"
							className="cursor-pointer rounded-2xl border-2 border-dashed border-gray-300 px-6 py-4 text-lg text-gray-600 hover:border-blue-400 hover:text-blue-500"
						>
							しゃしんをえらぶ
							<input
								id="file-upload-fallback"
								type="file"
								accept="image/*"
								className="hidden"
								onChange={onFileChange}
							/>
						</label>

						<button
							type="button"
							aria-label="やりなおす"
							className="min-h-[48px] rounded-2xl bg-gray-400 px-6 py-3 text-lg font-bold text-white shadow hover:bg-gray-500"
							onClick={reset}
						>
							やりなおす
						</button>
					</div>
				</div>
			)}
		</div>
	)
}
