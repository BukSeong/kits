## Markdown Base64 图片管理工具

适合经常写Markdown的学生党使用的Base64图片编码管理工具！

本项目包含两个 Python 脚本，用于在 Markdown 文件中管理 Base64 编码的图片。

### 1. `img2md.py` - 插入图片

该脚本用于将本地图片转换为 Base64 编码，并将其插入到 Markdown 文件的指定位置。

#### 功能特点
- **自动编码**：读取图片文件并转换为 Base64 字符串。
- **智能索引**：自动检测文档中已有的 `[image-N]` 标签，生成递增的唯一索引。
- **格式规范**：
  - 在指定行插入引用：`![Alt text][image-N]`
  - 在文档末尾追加定义：`[image-N]:data:image/png;base64,xxxx`
- **交互/命令行支持**：支持通过命令行参数运行，也支持交互式输入路径。

#### 使用方法

##### 命令行模式
```bash
python img2md.py --md-dir "path/to/doc.md" --img-dir "path/to/image.png" [选项]
```

**参数说明：**
- `--md-dir`: Markdown 文件的路径 (必填，可交互输入)。
- `--img-dir`: 图片文件的路径 (必填，可交互输入)。
- `-n`: 插入图片的行号 (从 1 开始)。如果不指定，默认插入到文档末尾。
- `--describe`: 图片的描述文字 (Alt text)，默认为 'Alt text'。

##### 示例
在第 5 行插入图片：
```bash
python img2md.py --md-dir "notes.md" --img-dir "screenshot.png" -n 5 --describe "示例截图"
```

---

### 2. `base64_manager.py` - 管理/删除图片

该脚本用于列出 Markdown 文档中所有的 Base64 图片定义，并支持删除指定的图片编码。

#### 功能特点
- **列出引用**：扫描文档，列出所有形如 `[image-N]:data:image/...` 的行及其行号。
- **批量删除**：支持一次性删除一个或多个图片定义。
- **安全检查**：如果指定的 ID 不存在，会给出警告。

#### 使用方法

##### 命令行模式
```bash
python base64_manager.py --md-dir "path/to/doc.md" [选项]
```

**参数说明：**
- `--md-dir`: Markdown 文件的路径 (必填，可交互输入)。
- `--idx`: 要删除的 image-id，支持用逗号或空格分隔多个 ID (例如 `image-1,image-2`)。如果不指定，将进入交互模式询问。

##### 示例
**1. 列出所有图片并交互式删除：**
```bash
python base64_manager.py --md-dir "notes.md"
```
输出示例：
```text
在 notes.md 中找到以下Base64图片引用:
- image-1 (行: 50)
- image-2 (行: 55)
输入要删除的image-id，可用逗号/空格分隔（回车跳过）：
```

**2. 直接删除指定 ID：**
```bash
python base64_manager.py --md-dir "notes.md" --idx "image-1 image-3"
```

### 依赖环境
- Python 3.x
- 标准库 (argparse, base64, os, re, sys) - 无需额外安装第三方库。
