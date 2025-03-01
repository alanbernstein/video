import subprocess

clips = [
    ["20250117_104649-fixed.mp4", 4, 15, "getting used to the chair lift"],
    ["20250117_104649-fixed.mp4", "1:14", "1:24", "huge drop on the double black"],
    # ["20250117_105347-fixed.mp4"], exiting lift
    ["20250117_105439-fixed.mp4", 0, 9, "trail map at the top"],
    # ["20250117_105556-fixed.mp4"], # looking around up top
    ["20250117_105630-fixed.mp4", 0, 15, "view at the top"],
    ["20250117_105757-fixed.mp4", 0, 32, "trail: recluse"],
    ["20250117_105757-fixed.mp4", "1:07", "1:18", "trail hub"],
    ["20250117_105954-fixed.mp4", 0, 54, "tight twisty section"],
    ["20250117_110248-fixed.mp4", 32, 42, "following some kid"],
    ["20250117_110248-fixed.mp4", "1:04", "1:20", "following some kid"],
    # ["20250117_111834-fixed.mp4"], # looking at map
    ["20250117_112026-fixed.mp4", 0, 44, "trail: antidote"],
    # ["20250117_112414-fixed.mp4"], # more antidote?
    # ["20250117_142513-fixed.mp4"], # itsy bitsy
    ["20250117_142820-fixed.mp4", "1:15", "2:00", "some minor air time"],
    ["20250117_143353-fixed.mp4", 0, 15, "double bike board"],
    # ["20250117_143851-fixed.mp4"], # view from lift
    # ["20250117_144136-fixed.mp4", 0, 15, "exiting lift"],
    # ["20250117_144408-fixed.mp4", 0, 44, "viper's den"],
    ["20250117_144514-fixed.mp4", 0, 30, "big bank fail"],
    ["20250117_144514-fixed.mp4", 40, 60, "trail: tarantula"],
    #["20250117_144515-fixed.mp4"], # tarantula clip extracted on phone
    ["20250117_150359-fixed.mp4", 0, 65, "trail: sidewinder"],
    # ["20250117_152315-fixed.mp4"], # recluse
    # ["20250117_152456-fixed.mp4"], # nothing good
    ["20250117_152525-fixed.mp4", 0, 52, "trail: recluse"],
    ["20250117_153853-fixed.mp4", 7, "1:52", "trail: sticky icky/cedar fever"],
]

def main():
    # create title
    title_filename = 'title.mp4'
    title_text = 'spider mountain 2025/01/17'
    title_duration = 3.0
    title_bgcolor = 'black'
    resolution = '1456x1936'     # TODO get resolution from input files
    cmd = [
        'ffmpeg',
        '-y',
        '-f', 'lavfi', '-i', 'color=color=%s:size=%s:duration=%s' % (title_bgcolor, resolution, title_duration),
        '-f', 'lavfi', '-t', '%s' % title_duration, '-i', 'anullsrc=r=44100:cl=stereo',
        '-vf', '"drawtext=text=\'%s\':x=(w-text_w)/2:y=(h-text_h)/2:fontcolor=white:fontsize=72:borderw=2:bordercolor=black"' % title_text,
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-t', '%s' % title_duration,
        '-pix_fmt', 'yuv420p',
        title_filename,
        '>>', 'ffmpeg_log.txt', '2>&1',
    ]
    cmd = ' '.join(cmd)
    subprocess.check_output(cmd, shell=True)

    # process clips
    USE_TITLE = False
    if USE_TITLE:
        n, ts_start, ts_end = 0, title_duration, title_duration
        filenames = [title_filename]
    else:
        n, ts_start, ts_end = 0, 0.0, 0.0
        filenames = []
    annotations = []
    for [fin, start, end, desc] in clips:
        start, end = parse_time(start), parse_time(end)
        dur = end - start
        ts_end = ts_start + dur
        annotations.append([ts_start, ts_end, desc])
        desc = desc.replace(':', '\:') # : is the delimiter for the drawtext syntax
        cmd = [
            'ffmpeg',
            '-y',                 # overwrite output automatically
            '-i', '%s' % fin,     # input file
            '-ss', '%s' % start,  # start time
            '-to', '%s' % end,    # end time
            '-c:v', 'libx264',    # re-encode video for more precise cuts
            '-c:a', 'aac',        # specify audio codec
            #'-filter_complex "pan=stereo|c0=c0|c1=c0"'  # replace right channel with left channel (for glitched RBM videos)
            '-vf', '"drawtext=text=\'%s\':x=(w-text_w)/2:y=4*(h-text_h)/5:fontcolor=white:fontsize=48:borderw=2:bordercolor=black"' % desc,
            '%02d.mp4' % n,
            '>', 'ffmpeg_log.txt', '2>&1',
        ]
        cmd = ' '.join(cmd)
        print(cmd)
        print('%02d: %s - %s' % (n, ts_start, ts_end))
        #subprocess.check_output(cmd, shell=True)
        filenames.append("%02d.mp4" % n)
        n += 1
        ts_start = ts_end

    # write annotations to a file
    print(annotations)
    with open('annotations.txt', 'w') as f:
        for a in annotations:
            f.write('%s %s %s\n' % tuple(a))
    
    # combine
    with open('splice_list.txt', 'w') as f:
        for c in filenames:
            f.write("file '%s'\n" % c)
    cmd = [
        'ffmpeg',
        '-y',
        '-f', 'concat',  # specify concatenation format
        '-safe', '0',    # allow relative or unsafe paths in list
        '-i', 'splice_list.txt',
        '-c:v', 'libx264',    # re-encode video for more precise cuts
        '-c:a', 'aac',        # specify audio codec
        'output.mp4',
        '>>', 'ffmpeg_log.txt', '2>&1',
    ]
    cmd = ' '.join(cmd)
    subprocess.check_output(cmd, shell=True)


def parse_time(t):
    if type(t) is str:
        parts = t.split(":")
        if len(parts) == 2:
            m = int(parts[0])
            s = float(parts[1])
            return 60*m + s

    if type(t) is float or type(t) is int:
        return t    

main()