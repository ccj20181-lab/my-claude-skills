#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io, os, base64, time
from pathlib import Path
import requests
from dotenv import load_dotenv

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

OUTPUT_DIR = 'F:/finance-infographics'

def get_api_config(api_choice='nanobanana'):
    load_dotenv(Path(__file__).parent.parent / '.env')
    if api_choice == 'google':
        api_key = os.environ.get('GOOGLE_API_KEY', '').strip()
        api_url = os.environ.get('GOOGLE_API_URL', '').strip()
    else:
        api_key = os.environ.get('NANO_BANANA_API_KEY', '').strip()
        api_url = os.environ.get('NANO_BANANA_API_URL', '').strip()
    if api_key and api_url:
        return api_url, api_key
    raise ValueError('API not configured')

def get_reference_images():
    ref_dir = Path(__file__).parent.parent / 'references'
    images = []
    for img_path in ref_dir.glob('*.png'):
        with open(img_path, 'rb') as f:
            b64 = base64.b64encode(f.read()).decode('utf-8')
            images.append({'mimeType': 'image/png', 'data': b64})
    return images

def generate(content, api_url, api_key, main_title):
    # 极简提示词：只告诉AI任务类型和内容
    prompt = '[IMAGE GENERATION TASK] Create a new infographic with this content. Match the style of the reference image exactly.'
    if main_title:
        prompt = '[IMAGE GENERATION TASK] Title: ' + main_title + '. Create new infographic with content below. Match reference style exactly.'
    prompt = prompt + chr(10) + chr(10) + content
    
    parts = []
    for img in get_reference_images():
        parts.append({'inlineData': img})
    parts.append({'text': prompt})
    
    payload = {'contents': [{'parts': parts}], 'generationConfig': {'responseModalities': ['IMAGE'], 'imageConfig': {'aspectRatio': '3:4', 'imageSize': '4K'}}}
    
    try:
        r = requests.post(api_url, headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + api_key}, json=payload, timeout=180)
        r.raise_for_status()
        data = r.json()
        if 'candidates' in data:
            for p in data['candidates'][0].get('content', {}).get('parts', []):
                if 'inlineData' in p:
                    return base64.b64decode(p['inlineData'].get('data', ''))
    except Exception as e:
        print('  [ERROR] ' + str(e))
    return None

def main():
    import argparse
    parser = argparse.ArgumentParser(description='批量生成财经信息图')
    parser.add_argument('md_files', nargs='+', help='md 文件路径列表')
    parser.add_argument('-r', '--resolution', default='2K', choices=['1K', '2K', '4K'], help='分辨率')
    parser.add_argument('--api', default='nanobanana', choices=['google', 'nanobanana'], help='API 选择')
    parser.add_argument('--topic', default='default', help='主题名称（创建文件夹）')
    parser.add_argument('--titles', nargs='+', help='主标题列表（与md文件对应）')
    parser.add_argument('-o', '--output', default=OUTPUT_DIR, help='输出目录')
    parser.add_argument('--interactive', action='store_true', help='交互式模式')
    args = parser.parse_args()

    api_url, api_key = get_api_config(args.api)
    md_files = args.md_files
    topic = args.topic
    titles = args.titles if args.titles else [Path(f).stem for f in md_files]

    # 确保 titles 和 md_files 数量一致
    if len(titles) < len(md_files):
        titles = titles + [Path(f).stem for f in md_files[len(titles):]]

    output_dir = Path(args.output) / topic
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime('%Y%m%d_%H%M%S')

    print('Generate ' + str(len(md_files)) + ' images...')
    for i, md_file in enumerate(md_files):
        title = titles[i] if i < len(titles) else Path(md_file).stem
        print('[ ' + str(i+1) + '/' + str(len(md_files)) + ' ] ' + title)
        content = Path(md_file).read_text(encoding='utf-8')
        data = generate(content, api_url, api_key, title)
        if data:
            path = output_dir / ('infographic_' + ts + '_' + format(i, '03d') + '.png')
            path.write_bytes(data)
            print('  [OK] ' + str(path))
        else:
            print('  [FAIL]')
        time.sleep(0.5)
    print('Done!')

if __name__ == '__main__':
    main()
