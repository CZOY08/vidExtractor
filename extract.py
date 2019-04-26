#!/usr/bin/python3

import do_extract
import config


if __name__ == "__main__":

    config = config.load_config()
    #print(config)
    vid_dir = config['vid_dir']
    #print(vid_dir)
    pic_dir = config['pic_dir']
    span = int(config['span'])
    column =int(config['column'])

    do_extract.main(vid_dir, pic_dir, span, column)
