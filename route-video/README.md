# 林口高中 → 桃園療養院 路線影片

- `林口高中_到_桃園療養院_輕量版.mp4`：1920×1080、30fps、64 秒
- `source/`：產生影片的原始檔
  - `prep.py`：讀取 OSRM 路線（osrm.json），計算距離與海拔，輸出 route.json
  - `data.js`：內嵌的路線資料
  - `index.html`：MapLibre 3D 地圖動畫（需同目錄放 maplibre-gl.js / .css 4.7.1）
  - `render.js`：Playwright 逐格截圖，`node render.js 0-640 frames`，再用 ffmpeg 合成

圖資：內政部國土測繪中心（電子地圖、正射影像）｜地形：Mapzen Terrain Tiles (AWS Open Data)｜路線：© OpenStreetMap contributors / OSRM
