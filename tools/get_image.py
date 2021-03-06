from PIL import Image, ImageDraw
import boto3
import sys
import argparse

BUCKET_NAME = '12306bucket'


def show_captcha(filename, row, col):
    s3 = boto3.client('s3')
    s3.download_file(BUCKET_NAME, filename, '/tmp/{}'.format(filename))
    im = Image.open('/tmp/{}'.format(filename))
    top = 41 + (67 + 5) * row
    left = 5 + (67 + 5) * col
    draw = ImageDraw.Draw(im)
    corner_size = 10
    draw.rectangle(((left, top), (left + 67, top + 67)), outline='red')
    draw.rectangle(((left, top),
                    (left + corner_size, top + corner_size)), fill='red')
    draw.rectangle(((left, top + 67 - corner_size),
                    (left + corner_size, top + 67)), fill='red')
    draw.rectangle(((left + 67 - corner_size, top + 67 - corner_size),
                    (left + 67, top + 67)), fill='red')
    draw.rectangle(((left + 67 - corner_size, top),
                    (left + 67, top + corner_size)), fill='red')

    return im


def search_captcha(path, phash, maximum=0):
    result = list()
    with open(path) as f:
        for line in f:
            if maximum and maximum < len(result):
                break
            if phash in line:
                content = line.strip().split('\t')
                filename = content[0]
                idx = content.index(phash)
                row, col = (idx - 2) // 8, (idx // 2 - 1) % 4
                result.append((filename, row, col))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--show", action="store_true",
                        help="specify the file path for text_captcha")
    parser.add_argument("-n", "--number", type=int,
                        default=0,
                        help="specify the maximum number of image to retrieve")
    parser.add_argument("text_captcha", action="store",
                        help="specify the file path for text_captcha")
    parser.add_argument("rgb_phash", action="store",
                        help="specify the phash value")
    args = parser.parse_args()
    for file_name, row, col in search_captcha(args.text_captcha, 
                                                args.rgb_phash,
                                                args.number):
        print "{} {} {}".format(file_name, row, col)
        if args.show:
            show_captcha(file_name, row, col).show()
