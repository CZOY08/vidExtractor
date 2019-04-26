#!/usr/bin/python3

import os
import sys
from ffmpy import FFmpeg
import subprocess
import re
import time
import PIL.Image as Image
import PIL.ImageFile as ImageFile
import shutil


def get_FileModifyTime(filePath):
    filePath = unicode(filePath, 'utf8')
    t = os.path.getmtime(filePath)
    return t


def get_members(file_dir, members=[]):  # root, dirs, files
    members = []
    list = []
    for root in os.walk(file_dir):
        # if root[0] == file_dir:
        #  continue
        # print(dir[0])#.split('/')[-1])
        list.append(root)
    # print(list[0][1])
    return list[0][1]


# if dir does not exist, create one
def make_dir(dir_to_create):
    if not os.path.exists(dir_to_create):
        os.makedirs(dir_to_create)
        return True
    else:
        return False


# if dir does not exist, pass, else, delete it
def del_dir(dir_to_del):
    if os.path.exists(dir_to_del):
        shutil.rmtree(dir_to_del)
        return True
    else:
        return False


# find out what is in a dir and return a list
def find_in_dir(dir, format):
    list = []
    for file in os.listdir(dir):
        if file.split('.')[-1] == format:
            list.append(file)
    return (list)


# compress the image
def compressImage(dir):
    pic_list = []

    for files in os.walk(dir):
        for file in files:
            pic_list.append(file)

    pic_list = pic_list[2]
    if pic_list == []:
        return True

    im = Image.open(dir + '/' + pic_list[0])
    width = im.size[0]
    height = im.size[1]

    if height <= 60:
        return True

    for pic in pic_list:
        image = Image.open(dir + '/' + pic)
        if height >= 720:
            rate = 0.1
        else:
            rate = 0.2
        new_width = int(width * rate)  # 新的宽
        new_height = int(height * rate)  # 新的高
        image.thumbnail((new_width, new_height), Image.ANTIALIAS)  # 生成缩略图
        image.save(dir + '/' + pic, 'JPEG')  # 保存到原路径


def get_length(filename):
    result = subprocess.Popen(["ffprobe", filename],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT)

    for x in result.stdout.readlines():
        if b"Duration" in x:
            print(x)
            x = re.search(rb"Duration.+?(\d{2}):(\d{2}):\d{2}", x)
            list = [int(x.group(1)), int(x.group(2))]
            return list


# cut and copress the image and save them in the folder
def cut(pic_cut_dir, video_dir, filename, video_format, span):
    real_video_dir = video_dir + '/' + filename + '.' + video_format
    print(real_video_dir)
    length = get_length(real_video_dir)

    minute = 0
    hour = 0
    count = 0
    while hour < length[0]:
        count += 1
        if hour < 10:
            if minute < 10:
                time = '0' + str(hour) + ':0' + str(minute) + ':01'
            else:
                time = '0' + str(hour) + ':' + str(minute) + ':01'
        else:
            if minute < 10:
                time = str(hour) + ':0' + str(minute) + ':01'
            else:
                time = str(hour) + ':' + str(minute) + ':01'

        if os.path.isfile(pic_cut_dir + '/' + str(count) + '.png'):
            print('pass ' + pic_cut_dir + '/' + str(count) + '.png')
            minute += span
            if minute >= 60:
                minute = minute % 60
                hour += 1
            continue

        ff = FFmpeg(
            inputs={real_video_dir: '-ss ' + time},
            outputs={pic_cut_dir + '/' + str(count) + '.png': '-f image2 -t 0.001 -y'}
        )

        ff.run()

        minute += span
        if minute >= 60:
            minute = minute % 60
            hour += 1

    while hour == length[0] and minute < length[1]:
        count += 1
        if hour < 10:
            if minute < 10:
                time = '0' + str(hour) + ':0' + str(minute) + ':01'
            else:
                time = '0' + str(hour) + ':' + str(minute) + ':01'
        else:
            if minute < 10:
                time = str(hour) + ':0' + str(minute) + ':01'
            else:
                time = str(hour) + ':' + str(minute) + ':01'

        if os.path.isfile(pic_cut_dir + '/' + str(count) + '.png'):
            print('pass ' + pic_cut_dir + '/' + str(count) + '.png')
            minute += span
            if minute >= 60:
                minute = minute % 60
                hour += 1
            continue

        try:
            ff = FFmpeg(
                inputs={real_video_dir: '-ss ' + time},
                outputs={pic_cut_dir + '/' + str(count) + '.png': '-f image2 -t 0.001 -y'}

            )
            ff.run()
        except:
            print('hour=' + str(hour))
        minute += span

    compressImage(pic_cut_dir)
    return True


def merge_pic(dir, pic_format, IMAGE_COLUMN):
    file_name = dir + ".png"

    pic_list = []

    for files in os.walk(dir):
        for file in files:
            pic_list.append(file)

    pic_list = pic_list[2]
    pic_list.sort(key=lambda x: int(x[:-4]))

    print("pic_list = " + str(pic_list))
    print('dir = ' + str(dir))

    if pic_list == []:
        return True

    im = Image.open(dir + '/' + pic_list[0])
    width = im.size[0]
    height = im.size[1]
    # print(height)
    #IMAGE_COLUMN = 6  # 图片间隔，也就是合并成一张图后，一共有几列
    IMAGE_ROW = len(pic_list) // IMAGE_COLUMN + 1  # 图片间隔，也就是合并成一张图后，一共有几行
    # print(IMAGE_ROW)

    if height * len(pic_list) // IMAGE_COLUMN > 65500:
        compressImage(dir)
        return (merge_pic(dir, pic_format, IMAGE_COLUMN))

    to_image = Image.new('RGB', (IMAGE_COLUMN * width, IMAGE_ROW * height))  # 创建一个新图

    for i in range(len(pic_list)):
        from_image = Image.open(dir + '/' + pic_list[i])
        to_image.paste(from_image, (i % IMAGE_COLUMN * width, i // IMAGE_COLUMN * height))

    try:
        to_image.save(file_name)  # 保存新图
    except IOError:
        ImageFile.MAXBLOCK = IMAGE_COLUMN * width * IMAGE_ROW * height
        to_image.save(file_name)  # 保存新图


# create pic(including create folder, cut pics, merge pics, del folder)
def create_pics(video_dir, sub_pic_dir, pic_to_create, video_format, pic_format, column, span):
    for dir in pic_to_create:
        # create folder for every video(only for cutting, will del)
        pic_cut_dir = sub_pic_dir + '/' + dir
        make_dir(pic_cut_dir)

        # cut pics
        cut(pic_cut_dir, video_dir, dir, video_format, span)

        # merge pics
        merge_pic(pic_cut_dir, pic_format, column)

        # del cutter folder
        del_dir(pic_cut_dir)


def del_pics(pic_list, sub_pic_dir, pic_format):
    for pic in pic_list:
        os.remove(sub_pic_dir + '/' + pic + '.' + pic_format)


def do_cut(video_dir, pic_dir, video_format, pic_format, column, span):
    # if pic_dir does not exist, create one
    make_dir(pic_dir)

    # devide the video_dir for creating sub_pic_dir
    sub_pic_dir = pic_dir + '/' + video_dir.split('/')[len(video_dir.split('/')) - 1]
    make_dir(sub_pic_dir)

    # find out what's in the video_dir and store it in a list
    video_content = find_in_dir(video_dir, video_format)
    video_name = []
    for item in video_content:
        video_name.append(os.path.splitext(item)[0])
    # print(video_name)
    if video_name == []:
        del_dir(sub_pic_dir)
        return False

    # find out what's in the sub_pic_dir and store it in a list
    sub_pic_content = find_in_dir(sub_pic_dir, pic_format)
    sub_pic_name = []
    for item in sub_pic_content:
        sub_pic_name.append(os.path.splitext(item)[0])
    # print(sub_pic_name)

    # find what's only in video_dir and add it to sub_pic_dir
    pic_to_create = [item for item in video_name if item not in sub_pic_name]
    print('to add ' + str(pic_to_create))
    create_pics(video_dir, sub_pic_dir, pic_to_create, video_format, pic_format, column, span)

    # find what's only in pic_dir and del the pic
    pic_to_del = [item for item in sub_pic_name if item not in video_name]
    print('to del ' + str(pic_to_del))
    del_pics(pic_to_del, sub_pic_dir, pic_format)


def cut_ctbrec(video_dir, pic_dir, video_format='m3u8', pic_format='png'):
    # if pic_dir does not exist, create one
    make_dir(pic_dir)

    # devide the video_dir for creating sub_pic_dir
    sub_pic_dir = pic_dir + '/' + video_dir.split('/')[-2]
    make_dir(sub_pic_dir)
    pic_cut_dir = sub_pic_dir + '/' + video_dir.split('/')[-1]
    make_dir(pic_cut_dir)

    # find out what's in the video_dir and store it in a list
    video_content = find_in_dir(video_dir, video_format)
    video_name = []
    for item in video_content:
        video_name.append(os.path.splitext(item)[0])
    # video_name.sort(key=lambda x:int(x.split('-')[-1].split('_')[-1]))
    print(video_name)
    if video_name == []:
        del_dir(pic_cut_dir)
        return False

    for vid in video_name:
        # real_video_dir = video_dir + '/' + vid+'.' + video_format
        cut(pic_cut_dir, video_dir, vid, video_format)
        merge_pic(pic_cut_dir, pic_format)
        del_dir(pic_cut_dir)


def main(vid_dir, pic_dir, span, column):


    members = get_members(vid_dir)
    print('ctb_members = '+str(members))

    video_format = 'mp4'
    pic_format = 'png'

    for member in members:
        do_cut(vid_dir + '/' + member, pic_dir, video_format, pic_format, column, span)

    pic_member = get_members(pic_dir)
    pic_member_to_del = [item for item in pic_member if item not in members]
    print(pic_member_to_del)
    for member in pic_member_to_del:
        del_dir(pic_dir + '/' + member)


if __name__ == "__main__":
    main()


