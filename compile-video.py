import os
import subprocess


def compile_videos(base_path, definitions, title_text, fix_audio=False):
    USE_TITLE = True
    DRY_RUN = False

    os.chdir(base_path)
    temp_dir = 'temp-ffmpeg/'
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)
    log_filename = temp_dir + "log.txt"

    # create title
    title_filename = temp_dir + 'title.mp4'
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
        '>>', log_filename, '2>&1',
    ]
    cmd = ' '.join(cmd)
    subprocess.check_output(cmd, shell=True)

    # process clips
    if USE_TITLE:
        n, ts_start, ts_end = 0, title_duration, title_duration
        filenames = [title_filename]
    else:
        n, ts_start, ts_end = 0, 0.0, 0.0
        filenames = []
    annotations = []
    for [fin, start, end, desc] in definitions:
        start, end = parse_time(start), parse_time(end)
        dur = end - start
        ts_end = ts_start + dur
        annotations.append([ts_start, ts_end, desc])
        desc = desc.replace(':', '\:') # : is the delimiter for the drawtext syntax
        # TODO: conditionally include things, like the audio glitch fix
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
            temp_dir + '%02d.mp4' % n,
            '>', log_filename, '2>&1',
        ]
        cmd = ' '.join(cmd)
        print(cmd)
        print('%02d/%02d: %s - %s' % (n, len(definitions), ts_start, ts_end))
        if not DRY_RUN:
            subprocess.check_output(cmd, shell=True)
        filenames.append(temp_dir + "%02d.mp4" % n)
        n += 1
        ts_start = ts_end

    # write annotations to a file
    print(annotations)
    with open(temp_dir + 'annotations.txt', 'w') as f:
        for a in annotations:
            f.write('%s %s %s\n' % tuple(a))
    
    # combine
    with open(temp_dir + 'splice_list.txt', 'w') as f:
        for c in filenames:
            f.write("file '%s'\n" % c)
    cmd = [
        'ffmpeg',
        '-y',
        '-f', 'concat',  # specify concatenation format
        '-safe', '0',    # allow relative or unsafe paths in list
        '-i', temp_dir + 'splice_list.txt',
        '-c:v', 'libx264',    # re-encode video for more precise cuts
        '-c:a', 'aac',        # specify audio codec
        'output.mp4',
        '>>', log_filename, '2>&1',
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


def main():
    # compile_videos('/media/tba/videos/2025/2025-01-17-spider-mountain/', spider_mountain_202501, "spider mountain 2025/01", fix_audio=True)
    compile_videos('/media/tba/videos/2025/2025-02-27-pedernales/', pedernales_202502, "pedernales falls 2025/02")

pedernales_202502 = [
    ["20250227_151251_19fb8b14.mp4", 14, 29, "tent setup"],
    # ["20250227_165358_98f2cde1.mp4", 0, 1, ""],
    ["20250227_165533_ea6a85a6.mp4", 12, 32, "rock hoppin"],
    ["20250227_165533_ea6a85a6.mp4", 45, 55, ""],
    ["20250227_165836_53bda939.mp4", 1, 14, ""],
    ["20250227_165836_53bda939.mp4", 72, 96, ""],
    ["20250227_170435_08ce21d1.mp4", 12, 38, ""],
    ["20250227_170435_08ce21d1.mp4", 48, 55, ""],
    ["20250227_170435_08ce21d1.mp4", 91, 101, ""],
    ["20250227_171214_6a1ecb11.mp4", 4, 15, ""],
    ["20250228_091027_a89fa6fe.mp4", 8, 20, "pedernales falls"],
    ["20250228_091027_a89fa6fe.mp4", 58, 68, "pedernales falls"],
    ["20250228_091027_a89fa6fe.mp4", 150, 165, "pedernales falls"],
    ["20250228_091332_a2c0fc7b.mp4", 35, 46, ""],
    ["20250228_092256_9d6f3f1f.mp4", 97, 125, ""],
    ["20250228_092256_9d6f3f1f.mp4", 143, 157, ""],
    # ["20250228_092752_435aef69.mp4", 0, 0, ""],
    ["20250228_092842_71acf59e.mp4", 13, 31, ""],
    ["20250228_094049_97b5ecfa.mp4", 0, 99, ""],
    ["20250228_094557_72e1f8b7.mp4", 25, 33, ""],
    ["20250228_112846_ebdd8027.mp4", 20, 31, "back home"],
    ["20250228_112846_ebdd8027.mp4", 44, 54, "back home"],
    #["20250228_113109_cdf8e0ef.mp4", 0, 1, ""],
]

spider_mountain_202501 = [
    # filename, start in seconds, end in seconds, caption, fixaudio flag
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

if __name__ == '__main__':
    main()
