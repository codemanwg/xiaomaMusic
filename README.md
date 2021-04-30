# xiaomaMusic
## 基于vue3和python构建的部署在树莓派上的音乐点歌平台

#### 使用场景：在办公室内，每个人都播放着自己的歌曲，想要拥有一个统一的入口去播放，添加，切换歌曲。只需要一台能运行linux的设备和一个音响，或者直接贡献你同事的电脑，就可以解决这个问题。


后端用到的库：
> websockets Crypto httpx pygame mutagen databases sqlalchemy aiosqlite
> 
在根目录下执行`python database.py`初始化数据库。前后端通过websocket通讯

前端都放在html文件夹中，使用的是vue3，版本为3.0.0，也可以通过cdn的方式引入`<script src="https://unpkg.com/vue@next"></script>`
![前端截图1](https://github.com/codemanwg/xiaomaMusic/blob/main/html/img/screenshot/1.png)

#### 前端界面操作
1. 点击搜索进入搜索界面，搜索接口使用了网易云的api，在vip_download中修改为你的网易云账号Cookie则可以下载，vip歌曲需要账号也是vip，点击下载即可
![前端截图3](https://github.com/codemanwg/xiaomaMusic/blob/main/html/img/screenshot/3.png)
2. 所有界面拖动歌曲到歌单即可添加歌曲到歌单
3. 歌单界面拖动歌曲即可在歌单中删除歌曲
4. 点击`+`号添加歌单
5. 底部可以切换模式：随机和列表循环，上一首，暂停，下一首，调节音量

## TODO
1. 搜索下载更多平台歌曲
