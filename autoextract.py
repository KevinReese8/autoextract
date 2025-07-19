import os 
import sys
import subprocess
import argparse
import shutil

DEFAULT_PASSWORD = "himengzhan.vip"

# 获取 7z.exe 的路径（兼容 PyInstaller）
def get_7z_path():
    base = getattr(sys, '_MEIPASS', os.path.abspath('.'))
    return os.path.join(base, '7z', '7z.exe')

# 判断是否为压缩文件（支持常见类型）
def is_archive_file(path):
    archive_exts = ['.zip', '.7z', '.rar', '.tar', '.gz', '.xz', '.bz2']
    return any(path.lower().endswith(ext) for ext in archive_exts)

# 尝试修正压缩文件的后缀
def fix_suffix(file_path):
    with open(file_path, 'rb') as f:
        sig = f.read(6)

    # 根据文件头识别格式
    if sig.startswith(b'PK'):
        new_path = file_path + '.zip'
    elif sig.startswith(b'7z'):
        new_path = file_path + '.7z'
    elif sig.startswith(b'Rar!'):
        new_path = file_path + '.rar'
    else:
        return file_path  # 无需修改

    if not os.path.exists(new_path):
        os.rename(file_path, new_path)
        print(f"[i] 文件后缀修改为: {new_path}")
    return new_path

# 调用 7z 解压
def extract_with_7z(file_path, output_dir):
    seven_zip = get_7z_path()
    os.makedirs(output_dir, exist_ok=True)

    # 增加密码参数 -p<密码>
    cmd = [seven_zip, 'x', file_path, f'-o{output_dir}', f'-p{DEFAULT_PASSWORD}', '-y']
    
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"[!] 解压失败: {file_path}")
        print(result.stderr)
        return False
    print(f"[+] 解压成功: {file_path} -> {output_dir}")
    return True

# 递归解压核心逻辑
def recursive_extract(file_path, base_output, layer=0):
    file_path = fix_suffix(file_path)
    output_dir = os.path.join(base_output, f"layer_{layer}")
    success = extract_with_7z(file_path, output_dir)
    if not success:
        return

    # 查找所有嵌套压缩文件并递归处理
    for root, _, files in os.walk(output_dir):
        for name in files:
            fpath = os.path.join(root, name)
            if is_archive_file(fpath):
                print(f"[i] 发现嵌套压缩包: {fpath}")
                recursive_extract(fpath, base_output, layer + 1)

def main():
    parser = argparse.ArgumentParser(description="递归解压工具（内置 7z，默认密码）")
    parser.add_argument("archive", help="要解压的压缩文件")
    args = parser.parse_args()

    input_path = os.path.abspath(args.archive)

    if not os.path.isfile(input_path):
        print("[!] 输入文件不存在")
        return

    # 自动使用压缩包所在的文件夹作为输出目录
    output_base = os.path.dirname(input_path)

    recursive_extract(input_path, output_base, layer=0)


if __name__ == "__main__":
    main()

