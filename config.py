import json
import sys
import os


config_loc = "configs/config.json"


# opens file, returns json dict, returns None if error
def load_config():

    try:
        with open(config_loc, "r") as f:
            return json.load(f)
    except Exception as e:
        print(e)
        if not os.path.exists(config_loc.split('.')[0]):
            os.makedirs(config_loc.split('/')[0])
            #print(config_loc.split('/')[0])
        f = open(config_loc, 'w')
        vid_dir = input('vid dir:')
        pic_dir = input('pic dir:')
        config_content = json.dumps({'vid_dir': vid_dir, 'pic_dir': pic_dir}, separators=(',', ': '))
        print(config_content)
        f.write(config_content)

# opens file, writes config, returns True on success, False on error
def save_config(config):
    try:
        with open(config_loc, "w+") as f:
            json.dump(config, f, indent=4)

        return True
    except Exception as e:
        print(e)
        sys.exit(-1)


