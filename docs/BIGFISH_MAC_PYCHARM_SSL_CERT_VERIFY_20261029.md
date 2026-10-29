# macOS PyCharm Python 3.11 HTTPS 根证书失败修复 · 2026-10-29

## 实际用户复现（不能推称大批量成功）

用户本机终端是 `/Users/masonliu/PycharmProjects/Wengua/venv/bin/python /Users/masonliu/PycharmProjects/Wengua/Wengua_BigFish_518400.py`，框架环境为 `/Library/Frameworks/Python.framework/Versions/3.11/`。之前缺 Node 自动下载在 `_official_url('https://nodejs.org/dist/index.json')` 触发 `urllib.error.URLError: [SSL: CERTIFICATE_VERIFY_FAILED] unable to get local issuer certificate`，具体触发来自 `ssl.SSLCertVerificationError`。它发生在首次安装阶段，**尚未有真实BigFish起盘、冻结V8断词或518400行计算**。不允许关闭证书校验或用 `verify=False`、`CERT_NONE` 规避。

## 无需换脚本的原生修法

在 Mac 终端执行 `open "/Applications/Python 3.11/Install Certificates.command"`（python.org macOS Python 3.11 的根证书安装捷径），随后重启或重跑 PyCharm。如果该路径不存在，用户可直接用本轮新脚本。公司 TLS 代理可能需要在 macOS 本身安装其可信根证书；不以跳过证书验证作为修法。

## 本轮真实交付

重新生成同名完整 `Wengua_BigFish_518400.py` 963 行/51315 字节，SHA256 `00033472598f2b5f49e54823c9acc95b817e0e6b6bd5f0a2e45f30694895ece8`；ZIP `Wengua_BigFish_518400_SSL证书修复_20261029.zip` SHA256 `27e9549175cb3568c310ae8f7f57335ec076148854aeb2df87252576ac16b480`。均为当前会话产生的沙盒文件；源码未伪称已经单独上传到GitHub main。保留原文件位置，和 `local_batch.py` 同层，覆盖旧py即可，原 `output` 与 `vendor`、`frozen` 不删。

新代码 `_verified_https_context()`：
1. 使用 `ssl.create_default_context()`，加载当前 PyCharm venv 可用的 `certifi.where()` 根CA；
2. macOS 进一步读取 Apple 官方 `/System/Library/Keychains/SystemRootCertificates.keychain` 根证书，用 `/usr/bin/security find-certificate -a -p` 导出并载入 TLS context；不执行网络获取来的代码，不禁用SSL验证；
3. 官方 Node `https://nodejs.org/dist/` 端点全部使用上述 context 验证TLS证书与hostname，并继续实施Node发布包官方SHA256的第二重校验、大小限额、安全解压；
4. 任何链验证失败转成明确的 Mac `Install Certificates.command` 提示，依旧安全停止。

## 实测
- `python -m py_compile /mnt/data/Wengua_BigFish_518400.py` PASS。
- `python -m unittest -v /mnt/data/test_bigfish_518400_nodefix.py /mnt/data/test_bigfish_518400_sslfix.py` **20/20 PASS**，其中原 13 项包括按关系枚举、干支派生、断点SQLite、CSV/XLSX与 SHA防篡改的 Node 本地模拟安装；新增7项包括默认SSLContext严格认证、官方urlopen显式传context、拒绝非官方站点、拒绝超限、模拟系统根证书装载、模拟验证失败的清晰提示、防止SSL绕过。全部网络/归档下载**为隔离模拟测试**，并未声称联网真实安装成功。
- ZIP经 zipfile.testzip() CRC PASS；源SHA已核对。

## 冻结边界
疾病轻重冻结 V8.0、200格和81表、人物来源、V10.2中文、Swift原生/iOS工程、Important镜像/MANIFEST、原书案例和历史失败完全不改。理论518400个四柱组合仍不是518400个都合法对应真实公历交节的时刻，双节气只是条件候选。未进行Mac真实联网安装、真实BigFish 518400大循环、Swift parity或Xcode/macOS编译；不能宣称通过。