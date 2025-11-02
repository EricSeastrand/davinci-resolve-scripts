
template_node_graph_drx=r'Y:\Resolve Powergrades\New Template 2025.drx'
global_look_drx=r'Y:\Resolve Powergrades\My CKC LUT Look 1_1.478.1.T.drx'

print("Got resolve")

projectmanager = resolve.GetProjectManager()
project        = projectmanager.GetCurrentProject()
mediapool      = project.GetMediaPool()
currentbin     = mediapool.GetCurrentFolder()
clips          = currentbin.GetClips()


def adjustTimeCodeByHours(oldTc, hours):
    # Example input 20:14:10:05
    tcParts = oldTc.split(':', 1)

    tcHours = int(tcParts[0])
    tcHoursNew = tcHours + hours

    newTc = str(tcHoursNew) + ':' + tcParts[1]
    return newTc

def getTimecodeFromModifyDate(modified):
    timeParts = modified.split(' ') # Ex: Sat Dec 25 19:53:13 2021

    modTime = timeParts[3]

    return modTime + ':00'

def parseDateModifiedToDateTime(date_string):
    # date_string = "Sat Apr 29 21:20:52 2023"
    from datetime import datetime

    date_format = "%a %b %d %H:%M:%S %Y"

    parsed_date = datetime.strptime(date_string, date_format)

    return parsed_date

def generateTimelineName(clip):
    date_string = clip.GetClipProperty("Date Modified")
    datetime = parseDateModifiedToDateTime(date_string)
    
    return datetime.strftime("%Y-%m-%d %a")

timelines_for_dates = {}

# Gather the clips...
for clip in clips.values():
    #allProps = clip.GetClipProperty()
    #print(allProps)
    #break
    filePath = clip.GetClipProperty("File Path")
    name = clip.GetClipProperty('Clip Name')

    if(not filePath):
        print("Skipping "+name+" because no filepath. Probably it's a timeline and not a clip")
        continue

    timeline_name = generateTimelineName(clip)

    if timeline_name not in timelines_for_dates:
        timelines_for_dates[timeline_name] = []

    timelines_for_dates[timeline_name].append(clip)


# Sort the timelines alphabetical
# ChatGPT made this magic oneliner for me. Sorcery or magic I'm not sure
timelines_for_dates = dict(sorted(timelines_for_dates.items(), key=lambda item: item[0]))

def handle_timeline_clip(video_clip):
    clip_node_graph = video_clip.GetNodeGraph()
    clip_node_graph.ApplyGradeFromDRX(template_node_graph_drx, 0)

def cleanup_timeline_clip(video_clip):
    source_camera = get_camera_name_for_clip(video_clip.GetMediaPoolItem())
    clip_node_graph = video_clip.GetNodeGraph()
    if source_camera == 'A7C':
        clip_node_graph.SetNodeEnabled(1, True)
    else:
        clip_node_graph.SetNodeEnabled(1, False)

def get_sort_value_for_clip(clip):
    "Allows us to apply an arbitrary time adjustment for when cameras' datetime was out of sync by a known amount"
    modified_time_str = clip.GetClipProperty("Date Modified")

    modified_time = parseDateModifiedToDateTime(modified_time_str)

    came_from_camera = get_camera_name_for_clip(clip)
    
    # if(came_from_camera == 'ZVE1'):
    #     from datetime import timedelta
    #     sony_offset = timedelta(hours=-1)
    #     modified_time = modified_time + sony_offset
    
    print(f"{came_from_camera=} {modified_time=} {modified_time_str=}")
    return modified_time


def get_camera_name_for_clip(clip):
    colorspace = clip.GetClipProperty('Input Color Space')
    camera_colorspaces = {
        'S-Gamut3/S-Log3': 'ZVE1',
        'S-Gamut/S-Log': 'A7C',
        'Rec.2020 (Scene)': 'iPhone'
    }

    return camera_colorspaces.get(colorspace, 'Other')


timelines_created = 0
timelines_to_create = len(timelines_for_dates)

# Create the timelines
for timeline_name, clips in timelines_for_dates.items():
    print(f"Creating {timelines_created+1} of {timelines_to_create} : {timeline_name}")

    clips = sorted(clips, key=lambda clip: get_sort_value_for_clip(clip))
    
    print(f"Creating: {timeline_name} with {len(clips)} clips.")
    mediapool.CreateTimelineFromClips(timeline_name, clips)

    timeline = project.GetCurrentTimeline()



    print("Created" + timeline.GetName())

    timeline_clips = timeline.GetItemListInTrack('video', 1)

    for clip in timeline_clips:
        handle_timeline_clip(clip)
        cleanup_timeline_clip(clip)
    
    # break
    # timeline_node_graph = timeline.GetNodeGraph()
    # timeline_node_graph.ApplyGradeFromDRX(template_node_graph_drx)

    # import time
    # time.sleep(2)
    timelines_created += 1

    # if timelines_created > 0:
    #     break

