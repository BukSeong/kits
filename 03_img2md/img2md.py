import argparse
import base64
import os
import re
import sys

def get_next_index(content):
    """
    扫描内容中已有的 [image-<idx>] 标签，返回下一个可用的序号。
    """
    # 匹配 [image-数字] 的模式
    matches = re.findall(r'\[image-(\d+)\]', content)
    if not matches:
        return 1
    
    # 将找到的数字转换为整数并找到最大值
    indices = [int(m) for m in matches]
    return max(indices) + 1

def get_mime_subtype(extension):
    """
    根据文件扩展名返回 MIME type 的子类型
    """
    ext = extension.lower().lstrip('.')
    if ext == 'jpg':
        return 'jpeg'
    # 对于 ico, png, gif 等，通常直接使用扩展名即可，或者根据需要调整
    # 标准 MIME: .ico -> x-icon, 但用户提示中写的是 <图片格式>，通常 image/png, image/jpeg 等
    return ext

def main():
    parser = argparse.ArgumentParser(description='将图片以Base64编码插入到Markdown文件中。')
    
    parser.add_argument('--md-dir', default=None, help='Markdown文件的路径')
    parser.add_argument('--img-dir', default=None, help='图片文件的路径')
    parser.add_argument('-n', type=int, default=None, help='插入图片的行号 (从1开始)。如果不指定，默认插入到最后。')
    parser.add_argument('--describe', default='Alt text', help='图片的描述文字 (Alt text)')

    args = parser.parse_args()

    md_path = args.md_dir
    img_path = args.img_dir

    # 检查参数，如果为None则请求输入
    if md_path is None:
        md_path = input("请输入Markdown文件路径 (--md-dir): ").strip()
    if img_path is None:
        img_path = input("请输入图片文件路径 (--img-dir): ").strip()

    # 去除可能存在的引号 (Windows复制路径时常带引号)
    md_path = md_path.strip('"\'')
    img_path = img_path.strip('"\'')

    # 验证文件存在性
    if not os.path.exists(md_path):
        print(f"错误: 找不到Markdown文件: {md_path}")
        return
    if not os.path.exists(img_path):
        print(f"错误: 找不到图片文件: {img_path}")
        return

    # 读取并编码图片
    try:
        with open(img_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"读取图片失败: {e}")
        return

    # 获取图片格式
    file_ext = os.path.splitext(img_path)[1]
    img_format = get_mime_subtype(file_ext)

    # 读取Markdown文件
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            content = "".join(lines)
    except Exception as e:
        print(f"读取Markdown文件失败: {e}")
        return

    # 获取下一个索引
    idx = get_next_index(content)
    
    # 构造插入文本
    ref_text = f"![{args.describe}][image-{idx}]"
    
    # 构造文末Base64块
    # 注意：按照要求在文档尾插入分隔符和#
    footer_block = f"\n\n--------\n#\n\n[image-{idx}]:data:image/{img_format};base64,{encoded_string}\n"

    # 插入引用文本
    if args.n is not None:
        # 转换为0-based索引
        insert_idx = max(0, args.n - 1)
        if insert_idx >= len(lines):
            # 如果指定行超过文件长度，追加到最后
            if lines and not lines[-1].endswith('\n'):
                lines.append('\n')
            lines.append(ref_text + "\n")
        else:
            # 插入到指定行
            lines.insert(insert_idx, ref_text + "\n")
    else:
        # 默认插入到文件最后一行 (在Base64块之前)
        if lines and not lines[-1].endswith('\n'):
            lines.append('\n')
        lines.append(ref_text + "\n")

    # 追加Base64数据块到文档末尾
    lines.append(footer_block)

    # 写回文件
    try:
        with open(md_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"成功处理！图片已插入到 {md_path}")
        print(f"索引 ID: image-{idx}")
    except Exception as e:
        print(f"写入文件失败: {e}")

if __name__ == "__main__":
    main()