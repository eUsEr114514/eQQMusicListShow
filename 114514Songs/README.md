# 114514Songs

在线访问：https://electrondz75.top/eQQMusicListShow/ （GitHub Pages）

QQ音乐歌单 `114514123` 的本地化版本：778 首完整音频 + 778 张封面 + 一个纯静态播放页。

- 打开网页：双击 [index.html](index.html)
- 使用说明：[使用说明.md](../使用说明.md)
- 改造文档：[开发说明.md](开发说明.md)
- 曲目清单：[下载清单.csv](下载清单.csv)

```
index.html     页面主体（结构 + 交互脚本）
styles/        base.css / cards.css / player.css
data/          tracks.js（曲目数组，顺序即展示顺序）
SongsFiles/    音频 {编号}-{歌名}.mp3|.flac
SongsCover/    封面 {编号}-{歌名}.jpg
```

音质构成：FLAC 49 首、MP3 320 kbps 648 首、MP3 128 kbps 81 首；单文件均小于 25 MB，合计约 6.25 GB。
