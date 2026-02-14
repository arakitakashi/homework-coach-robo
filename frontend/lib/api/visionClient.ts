/**
 * 画像認識APIクライアント
 *
 * バックエンドの画像認識APIを呼び出すクライアント。
 * カメラ撮影またはファイルアップロードされた画像を送信し、
 * 問題文テキストを抽出する。
 */

import type { ImageRecognitionRequest, ImageRecognitionResponse } from "@/types"

/** VisionClientのオプション */
export interface VisionClientOptions {
	/** バックエンドのベースURL */
	baseUrl?: string
}

/**
 * 画像認識APIクライアント
 *
 * @example
 * ```typescript
 * const client = new VisionClient({ baseUrl: "http://localhost:8000" })
 * const result = await client.recognizeImage({
 *   imageData: "base64...",
 *   mimeType: "image/jpeg"
 * })
 * ```
 */
export class VisionClient {
	private readonly baseUrl: string

	constructor(options?: VisionClientOptions) {
		this.baseUrl = options?.baseUrl ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"
	}

	/**
	 * 画像を認識して問題文を抽出する
	 *
	 * @param request - 画像認識リクエスト（Base64画像データ + MIMEタイプ）
	 * @returns 認識結果（テキスト、問題タイプ、確信度）
	 * @throws {Error} HTTPエラーまたはネットワークエラー時
	 */
	async recognizeImage(request: ImageRecognitionRequest): Promise<ImageRecognitionResponse> {
		const response = await fetch(`${this.baseUrl}/api/v1/vision/recognize`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify(request),
		})

		if (!response.ok) {
			throw new Error(
				`がぞうのよみとりにしっぱいしました: ${response.status} ${response.statusText}`,
			)
		}

		return response.json()
	}
}
