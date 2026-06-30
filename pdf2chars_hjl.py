import fitz  # PyMuPDF
import os
from PIL import Image
from tqdm import tqdm



# pdf_url = "https://www.unicode.org/charts/PDF/U3400.pdf"
# pdf_path = "U2FF0.pdf"

# # 下载 PDF（如果本地不存在）
# response = requests.get(pdf_url)
# with open(pdf_path, "wb") as f:
#     f.write(response.content)

def get_all_unicodes():
    list1 = []
    txt_path = r'D:\pdf2jpg\unicodes.txt'

    with open(txt_path, 'r', encoding='utf-8') as f1:
        lines = f1.readlines()
        for line in lines:
            arr = line.split('\t')
            unicode = arr[2]
            unicode = unicode.replace('U+', '')
            list1.append(unicode.strip())
    return list1


def get_unicode_x_list(col_count):
    if col_count == 3:
        list1 = [368.94000244140625, 220.13999938964844, 71.33999633789062, 103.26000213623047, 252.05999755859375,
                 400.8599853515625]
    elif col_count == 2:
        list1 = [326.4599914550781, 103.26000213623047, 71.33999633789062, 294.5400085449219]
    elif col_count == 4:
        list1 = [103.26000213623047, 214.86000061035156, 326.4599914550781, 438.05999755859375]
        list2 = [71.33999633789062, 182.94000244140625, 294.5400085449219, 406.1400146484375]
        list1.extend(list2)

    return list1


def box_overlap(box1, box2, only_check=False):
    """计算两个框的交叉面积和比例。如果only_check为True，则只要交叉就返回True"""
    x1, y1, w1, h1 = box1['x'], box1['y'], box1['w'], box1['h']
    x2, y2, w2, h2 = box2['x'], box2['y'], box2['w'], box2['h']
    if x1 > x2 + w2 or x2 > x1 + w1 or y1 > y2 + h2 or y2 > y1 + h1:
        return False if only_check else (0, 0, 0)

    if only_check or not (w1 and w2 and h1 and h2):
        return True if only_check else (0, 0, 0)
    else:
        col = abs(min(x1 + w1, x2 + w2) - max(x1, x2))
        row = abs(min(y1 + h1, y2 + h2) - max(y1, y2))
        overlap = col * row
        ratio1 = round(overlap / (w1 * h1), 2)
        ratio2 = round(overlap / (w2 * h2), 2)
        return overlap, ratio1, ratio2


def get_unicode_by_spans(span, spans):
    index = spans.index(span)
    spans2 = spans[0:index]

    # 反向遍历 spans2，找到最后一个符合条件的元素
    for s in reversed(spans2):
        if s.get('is_unicode'):
            return s.get('text')
    return ''  # 如果没有符合条件的则返回空字符串



def get_character_coordinates(pdf_path):
    pdf_document = fitz.open(pdf_path)
    # 获取文件名（含扩展名）
    filename_with_ext = os.path.basename(pdf_path)  # "report.pdf"

    # 分离文件名和扩展名
    pdf_name = os.path.splitext(filename_with_ext)[0]  # "report"
    if pdf_name in ['U20000', 'U2A700', 'U2B740', 'U2B820', 'U2CEB0', 'U2EBF0', 'U30000', 'U31350', ]:
        m = 4
    elif pdf_name in ['U2F800', 'U3400', 'UF900']:
        m = 3
    elif pdf_name in ['U4E00']:
        m = 2

    unicode_x_list = get_unicode_x_list(m)


    unicodes = get_all_unicodes()
    for page_num in range(len(pdf_document)):

        if page_num < 1:
            continue


        page = pdf_document.load_page(page_num)

        # 获取页面字符级数据（包含坐标）
        char_data = page.get_text("dict")  # 返回字典结构

        all_spans = []
        all_chars = []
        # 遍历所有字符块
        coordinates = []
        n = 0
        for i, block in enumerate(char_data["blocks"]):
            # if i == '170':
            #     print('')
            if "lines" in block:
                for j, line in enumerate(block["lines"]):
                    for k, span in enumerate(line["spans"]):
                        n += 1
                        x, y, x1, y1 = span["bbox"]
                        w = x1 - x
                        h = y1 - y
                        span['n'] = n
                        span['w'] = w
                        span['h'] = h

                        if x in unicode_x_list:
                            if span['text'] in unicodes:
                                span['is_unicode'] = True
                        if not span['text'].strip():
                            if w > 18 and h > 19:
                                pass
                            else:
                                continue

                        all_spans.append(span)
                        all_chars.append(
                            {'id': f'{i}{j}{k}', 'n': n, 'x': x, 'y': y, 'w': w, 'h': h, 'text': span['text']})

        for i, block in enumerate(char_data["blocks"]):

            if "lines" in block:
                for j, line in enumerate(block["lines"]):
                    for k, span in enumerate(line["spans"]):
                        if not span['text'].strip():
                            if span['w'] > 18 and span['h'] > 18:
                                pass
                            else:
                                continue

                        x0, y0, x1, y1 = span["bbox"]
                        w = x1 - x0
                        h = y1 - y0
                        if len(span['text']) == 1 and w > 18 and h > 18:
                            # print(span)
                            unicode = get_unicode_by_spans(span, all_spans)
                            span['unicode'] = unicode
                            index = all_spans.index(span)
                            next_span = all_spans[index + 1]
                            next_span_txt = next_span['text']
                            if len(next_span["text"]) > 1 and next_span["text"][-1] == '-':
                                next_span2 = all_spans[index + 2]
                                next_span2_txt = next_span2['text']
                                next_span_txt += next_span2_txt
                            span['name'] = f'{unicode}_{next_span_txt}'
                            span['next_span'] = next_span

        # 遍历所有字符块
        n = 0
        for i, block in enumerate(char_data["blocks"]):
            if "lines" in block:
                for j, line in enumerate(block["lines"]):
                    for k, span in enumerate(line["spans"]):
                        n += 1
                        if not span['text'].strip():
                            if span['w'] > 18 and span['h'] > 18:
                                pass
                            else:
                                continue
                        x0, y0, x1, y1 = span["bbox"]

                        w = x1 - x0
                        h = y1 - y0
                        origin_y = span['origin'][1]
                        y0 = origin_y - span['size']
                        if len(span['text']) == 1 and w > 18 and h > 18:

                            unicode = span['unicode']
                            if unicode == '27984':
                                print(unicode)

                            index = all_spans.index(span)
                            next_span = all_spans[index + 1]

                            next_span_txt = next_span['text']
                            if len(next_span_txt.strip())<2:
                                continue
                            if len(next_span["text"]) > 1 and next_span["text"][-1] == '-':
                                next_span2 = all_spans[index + 2]
                                next_span2_txt = next_span2['text']
                                next_span_txt += next_span2_txt

                            ch = {'id': f'{i}{j}{k}', 'x': x0, 'y': y0, 'w': x1 - x0, 'h': y1 - y0}
                            ch_y0= ch['y']
                            for char in all_chars:
                                if ch['id'] != char['id']:
                                    is_over = box_overlap(ch, char, True)

                                    if is_over:
                                        if n > char['n']:
                                            y0 = char['y'] + char['h']

                            next_span_y1 = span['next_span']['bbox'][1]
                            y1 = next_span_y1 + 0.9
                            w = x1 - x0
                            h = y1 - y0
                            if h<18:
                                y0=ch_y0
                                h = y1 - y0

                            x0 = x0 - 1
                            x1 = x1 + 1

                            if y0 < 80:
                                y0 = 80

                            print(pdf_name,page_num,'\t',span['name'])

                            coordinates.append({
                                "unicode": unicode,
                                "standard": next_span_txt,
                                "page": page_num + 1,
                                "x": (x0 + x1) / 2,  # 取中心坐标
                                "y": (y0 + y1) / 2,
                                "bbox": (x0, y0, x1, y1)
                            })



        #  截取字符区域
        # continue
        for coord in coordinates:

            page = pdf_document.load_page(coord["page"] - 1)
            # 计算缩放因子，确保输出图像的宽度和高度都达到500像素
            # 这里假设 coord["bbox"] 是适当的边界框
            width = coord["bbox"][2] - coord["bbox"][0]
            height = coord["bbox"][3] - coord["bbox"][1]
            print(coord['unicode'],width,height)

            scale_factor = 16

            # 使用更高的缩放因子
            matrix = fitz.Matrix(scale_factor, scale_factor).prescale(2, 2)  # 2倍抗锯齿

            pix = page.get_pixmap(matrix=matrix, clip=coord["bbox"])
            save_path = f'D:/pdf2jpg/data/unicode/{pdf_name}/{page_num}/'
            if not os.path.exists(save_path):
                os.makedirs(save_path, exist_ok=True)  # exist_ok=True 避免路径已存在时报错
            pix.save(f"{save_path}/{coord['unicode']}_{coord.get('standard')}.jpg")



def get_chars():
    list1 = ['UF900', 'U2A700', 'U2B740', 'U2B820', 'U2CEB0', 'U2E80', 'U2EBF0', 'U2F00', 'U2F800', 'U2FF0', 'U31350',
             'U31C0', 'U3400', 'U30000', 'U4E00', ]
    # list1 = ['U20000','U2A700','U2B740','U2B820','U2CEB0','U30000']
    list1 = ['U2A700',
'U2B820',
'U2CEB0',
'U2F800',
'U30000',
]
    for li in list1:
        if li in ['U2E80', 'U2F00', 'U2FF0', 'U31C0']:
            continue
        pdf_path = f'D:/pdf2jpg/pdf/{li}.pdf'
        get_character_coordinates(pdf_path)


def get_chars2():
    list1 = ['U20000', ]
    for li in list1:
        if li in ['U2E80', 'U2F00', 'U2FF0', 'U31C0']:
            continue
        pdf_path = f'D:/pdf2jpg/pdf/{li}.pdf'

        results = get_character_coordinates(pdf_path)


def get_chars3():
    for li in ['U2E80', 'U31C0', 'U2FF0', 'U2F00', ]:
        pdf_path = f'D:/pdf2jpg/pdf/{li}.pdf'

        results = get_character_coordinatesw2(pdf_path)


def get_character_coordinatesw2(pdf_path):
    pdf_document = fitz.open(pdf_path)
    # 获取文件名（含扩展名）
    filename_with_ext = os.path.basename(pdf_path)  # "report.pdf"

    # 分离文件名和扩展名
    pdf_name = os.path.splitext(filename_with_ext)[0]  # "report"

    if pdf_name == 'U2E80':
        unicode_x_range = range(204, 427)
    elif pdf_name == 'U2F00':
        unicode_x_range = range(78, 490)
    elif pdf_name == 'U2FF0':
        unicode_x_range = range(204, 205)
    elif pdf_name == 'U31C0':
        unicode_x_range = range(252, 316)
    codes = []
    unicodes = get_all_unicodes()
    for page_num in range(len(pdf_document)):
        if page_num not in [1]:
            continue

        page = pdf_document.load_page(page_num)

        # 获取页面字符级数据（包含坐标）
        char_data = page.get_text("dict")  # 返回字典结构

        all_spans = []
        all_chars = []
        # 遍历所有字符块
        coordinates = []
        n = 0
        for i, block in enumerate(char_data["blocks"]):
            # if i == '170':
            #     print('')
            if "lines" in block:
                for j, line in enumerate(block["lines"]):
                    for k, span in enumerate(line["spans"]):
                        n += 1
                        x, y, x1, y1 = span["bbox"]
                        w = x1 - x
                        h = y1 - y
                        span['n'] = n
                        span['w'] = w
                        span['h'] = h
                        if x in unicode_x_range and h < 7:
                            if span['text'] in unicodes:
                                span['is_unicode'] = True
                        all_spans.append(span)
                        all_chars.append(
                            {'id': f'{i}{j}{k}', 'n': n, 'x': x, 'y': y, 'w': w, 'h': h, 'text': span['text']})
                        print(page_num, f'{i}{j}{k}', x, y, w, h, span['text'])
        for span in all_spans:
            if span['bbox'][0] in unicode_x_range:
                if span['text'] in unicodes:
                    codes.append(span['text'])

        for i, block in enumerate(char_data["blocks"]):

            if "lines" in block:
                for j, line in enumerate(block["lines"]):
                    for k, span in enumerate(line["spans"]):
                        x0, y0, x1, y1 = span["bbox"]
                        w = x1 - x0
                        h = y1 - y0
                        if len(span['text']) == 1 and w > 18 and h > 19:
                            print(span)
                            ch = {'id': f'{i}{j}{k}', 'x': x0, 'y': y0, 'w': x1 - x0, 'h': y1 - y0 + 5}
                            for char in all_chars:
                                if ch['id'] != char['id']:
                                    is_over = box_overlap(ch, char, True)
                                    if is_over:
                                        unicode = char['text']
                                        span['unicode'] = unicode
                                        span['name'] = f'{unicode}_None'
                                        print(unicode)


        # 遍历所有字符块
        n = 0
        for i, block in enumerate(char_data["blocks"]):
            # if i == '170':
            #     print('')
            if "lines" in block:
                for j, line in enumerate(block["lines"]):
                    for k, span in enumerate(line["spans"]):
                        n += 1
                        x0, y0, x1, y1 = span["bbox"]
                        w = x1 - x0
                        h = y1 - y0
                        origin_y = span['origin'][1]
                        y0 = origin_y - span['size']
                        if len(span['text']) == 1 and w > 18 and h > 19:
                            unicode = span['unicode']

                            print(page_num, '\t', i, j, k, span["text"], '\t', (x0, y0, w, h), '\t', span['font'], '\t',
                                  span['size'], '\t', span['origin'], '\t', span['name'])

                            coordinates.append({
                                "unicode": unicode,
                                "standard": 'None',
                                "page": page_num + 1,
                                "x": (x0 + x1) / 2,  # 取中心坐标
                                "y": (y0 + y1) / 2,
                                "bbox": (x0, y0, x1, y1)
                            })
        # continue
        for coord in coordinates:

            page = pdf_document.load_page(coord["page"] - 1)

            scale_factor = 16

            # 使用更高的缩放因子
            matrix = fitz.Matrix(scale_factor, scale_factor).prescale(2, 2)  # 2倍抗锯齿

            pix = page.get_pixmap(matrix=matrix, clip=coord["bbox"])

            save_path = f'D:/pdf2jpg/data/unicode/{pdf_name}/{page_num}/'

            if not os.path.exists(save_path):
                os.makedirs(save_path, exist_ok=True)  # exist_ok=True 避免路径已存在时报错
            pix.save(f"{save_path}/{coord['unicode']}_{coord.get('standard')}.jpg")

    return coordinates

def case1():
    get_chars()
    get_chars2()
    get_chars3()

def main(func='case1', **kwargs):
    eval(func)(**kwargs)


if __name__ == '__main__':
    import fire

    fire.Fire(main)
