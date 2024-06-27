#!C:\Python3\python.exe

import DaVinciResolveScript as dvr_script
resolve = dvr_script.scriptapp("Resolve")

template_node_graph_drx=r'Y:\Resolve Powergrades\New Template 2024.drx'
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

# Create the timelines
for timeline_name, clips in timelines_for_dates.items():
    print(f"Sorting {timeline_name}")

    clips = sorted(clips, key=lambda clip: clip.GetClipProperty("Date Modified"))

    print(f"Creating: {timeline_name} with {len(clips)} clips.")
    mediapool.CreateTimelineFromClips(timeline_name, clips)

    timeline = project.GetCurrentTimeline()



    print("Created" + timeline.GetName())

    timeline_clips = timeline.GetItemListInTrack('video', 1)

    timeline.ApplyGradeFromDRX(template_node_graph_drx, 0, timeline_clips)
    timeline.ApplyGradeFromDRX(global_look_drx)

    import time
    time.sleep(2)

