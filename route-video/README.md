# 林口高中 → 桃園療養院 路線影片

- `林口高中_到_桃園療養院_輕量版.mp4`：1920×1080、30fps、64 秒
- `source/`：產生影片的原始檔
  - `prep.py`：讀取 OSRM 路線（osrm.json），計算距離與海拔，輸出 route.json
  - `data.js`：內嵌的路線資料
  - `index.html`：MapLibre 3D 地圖動畫（需同目錄放 maplibre-gl.js / .css 4.7.1）
  - `render.js`：Playwright 逐格截圖，`node render.js 0-640 frames`，再用 ffmpeg 合成

圖資：內政部國土測繪中心（電子地圖、正射影像）｜地形：Mapzen Terrain Tiles (AWS Open Data)｜路線：© OpenStreetMap contributors / OSRM

## 配樂
- `林口高中_到_桃園療養院_配樂版.mp4`：加入背景音樂的版本（建議上傳 YouTube 用這支）
- `source/make_music.py`：背景音樂以程式自行合成（96 BPM、C 大調，C–G–Am–F），沒有使用任何第三方音源，無版權問題。
  重新產生：`python3 source/make_music.py music.wav`，再用 ffmpeg 合成：
  `ffmpeg -i 影片.mp4 -i music.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -af loudnorm=I=-16:TP=-1.5 -shortest 輸出.mp4`
