# Design - CameraInterface (Issue #153)

## アーキテクチャ概要

ローカル状態（カメラストリーム・プレビュー）+ Jotai atom（認識結果）のハイブリッド。

## ファイル構成

- `types/vision.ts` - CameraStatus, CameraError 等
- `store/atoms/camera.ts` - cameraStatusAtom, cameraRecognitionAtom
- `lib/api/visionClient.ts` - VisionClient
- `components/features/CameraInterface/` - コンポーネント + フック

## 6状態の画面遷移

initial → active → preview → processing → recognized
各状態からerrorに遷移可能、error/recognizedからretakeでactiveに戻る
