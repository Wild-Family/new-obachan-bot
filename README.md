# オバチャンが撮ったるで！ Autumn Edition
## Botサーバ
### メモ
- AzureのMessage Busを用いたキューサーバ
- Raspberry Piからカメラ状況を受け取りLINEに送信するREST APIサーバも兼任
- アップロードされた写真のURL: `https://obachanbot.blob.core.windows.net/pic/{pic_name}`