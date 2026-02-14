/**
 * カメラキャプチャ管理フック
 *
 * カメラストリームのライフサイクル管理、画像キャプチャ、
 * ファイルアップロード、画像認識APIの呼び出しを統合的に管理する。
 *
 * 6状態の遷移:
 * initial → active → preview → processing → recognized
 * 各状態からerrorに遷移可能
 * error/recognized/preview → retake → active
 */

import { useCallback, useEffect, useRef, useState } from "react"
import { VisionClient } from "@/lib/api/visionClient"
import type { CameraError, CameraStatus, ImageRecognitionResponse } from "@/types"

/** useCameraCaptureの戻り値 */
export interface UseCameraCaptureReturn {
	/** カメラの現在の状態 */
	status: CameraStatus
	/** エラー情報（エラー時のみ） */
	error: CameraError | null
	/** キャプチャした画像のBase64データ */
	capturedImage: string | null
	/** 画像認識結果 */
	recognitionResult: ImageRecognitionResponse | null
	/** カメラを起動する */
	startCamera: () => Promise<void>
	/** 画像をキャプチャする */
	captureImage: () => void
	/** 撮り直す（カメラを再起動） */
	retake: () => Promise<void>
	/** 画像認識を実行する */
	recognizeImage: () => Promise<void>
	/** すべての状態をリセットする */
	reset: () => void
	/** ファイルアップロードで画像を取得する */
	handleFileUpload: (file: File) => void
	/** ビデオ要素のref */
	videoRef: React.RefObject<HTMLVideoElement | null>
}

/**
 * エラー種別に応じたメッセージを生成する（子供向けやさしい日本語）
 */
function createCameraError(error: unknown): CameraError {
	if (error instanceof DOMException) {
		switch (error.name) {
			case "NotAllowedError":
				return {
					type: "permission_denied",
					message: "カメラがつかえないよ。せってい をかくにんしてね",
				}
			case "NotFoundError":
				return {
					type: "not_available",
					message: "このデバイスにはカメラがないみたい",
				}
			default:
				return {
					type: "capture_failed",
					message: "しゃしんがうまくとれなかったよ。もういちどためしてね",
				}
		}
	}
	return {
		type: "unknown",
		message: "しゃしんがうまくとれなかったよ。もういちどためしてね",
	}
}

/**
 * カメラキャプチャ管理フック
 *
 * @returns カメラ操作のための関数と状態
 */
export function useCameraCapture(): UseCameraCaptureReturn {
	const [status, setStatus] = useState<CameraStatus>("initial")
	const [error, setError] = useState<CameraError | null>(null)
	const [capturedImage, setCapturedImage] = useState<string | null>(null)
	const [recognitionResult, setRecognitionResult] = useState<ImageRecognitionResponse | null>(null)

	const videoRef = useRef<HTMLVideoElement | null>(null)
	const streamRef = useRef<MediaStream | null>(null)
	const visionClientRef = useRef<VisionClient>(new VisionClient())

	/** メディアストリームのトラックを停止する */
	const stopStream = useCallback(() => {
		if (streamRef.current) {
			for (const track of streamRef.current.getTracks()) {
				track.stop()
			}
			streamRef.current = null
		}
	}, [])

	/** カメラを起動する */
	const startCamera = useCallback(async () => {
		try {
			const stream = await navigator.mediaDevices.getUserMedia({
				video: { facingMode: "environment" },
				audio: false,
			})
			streamRef.current = stream

			setError(null)
			setStatus("active")
		} catch (err) {
			setError(createCameraError(err))
			setStatus("error")
		}
	}, [])

	/** 画像をキャプチャする（Canvas経由） */
	const captureImage = useCallback(() => {
		if (!videoRef.current) return

		const canvas = document.createElement("canvas")
		canvas.width = videoRef.current.videoWidth
		canvas.height = videoRef.current.videoHeight

		const ctx = canvas.getContext("2d")
		if (ctx) {
			ctx.drawImage(videoRef.current, 0, 0)
		}

		const dataUrl = canvas.toDataURL("image/jpeg", 0.8)
		setCapturedImage(dataUrl)
		setStatus("preview")
	}, [])

	/** 撮り直す */
	const retake = useCallback(async () => {
		setCapturedImage(null)
		setRecognitionResult(null)
		setError(null)

		// カメラストリームを再起動
		if (streamRef.current) {
			// 既存ストリームがあればそのまま使う
			if (videoRef.current) {
				videoRef.current.srcObject = streamRef.current
			}
			setStatus("active")
		} else {
			// ストリームがなければ新規起動
			await startCamera()
		}
	}, [startCamera])

	/** 画像認識を実行する */
	const recognizeImage = useCallback(async () => {
		if (!capturedImage) return

		setStatus("processing")

		try {
			// Base64データ部分のみ抽出（data:image/jpeg;base64, を除去）
			const base64Data = capturedImage.split(",")[1] || capturedImage
			const mimeType = capturedImage.match(/data:(.*?);/)?.[1] || "image/jpeg"

			const result = await visionClientRef.current.recognizeImage({
				imageData: base64Data,
				mimeType,
			})

			setRecognitionResult(result)
			setStatus("recognized")
		} catch {
			setError({
				type: "recognition_failed",
				message: "もんだいをよみとれなかったよ。もういちどとってみてね",
			})
			setStatus("error")
		}
	}, [capturedImage])

	/** ファイルアップロードで画像を取得する */
	const handleFileUpload = useCallback((file: File) => {
		const reader = new FileReader()
		reader.onload = () => {
			const dataUrl = reader.result as string
			setCapturedImage(dataUrl)
			setStatus("preview")
		}
		reader.readAsDataURL(file)
	}, [])

	/** すべての状態をリセットする */
	const reset = useCallback(() => {
		stopStream()
		setStatus("initial")
		setError(null)
		setCapturedImage(null)
		setRecognitionResult(null)
	}, [stopStream])

	/** active状態になったときにvideo要素にストリームを接続 */
	useEffect(() => {
		if (status === "active" && streamRef.current && videoRef.current) {
			videoRef.current.srcObject = streamRef.current
		}
	}, [status])

	/** クリーンアップ: アンマウント時にストリームを停止 */
	useEffect(() => {
		return () => {
			stopStream()
		}
	}, [stopStream])

	return {
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
	}
}
