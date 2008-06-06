import mutagen, mutagen.id3, mutagen.mp3
from xl import common

TYPE = 'mp3'
IDS = { 
        "TIT2": "title",
        "TIT3": "version",
        "TPE1": "artist",
        "TPE2": "performer",
        "TPE3": "conductor",
        "TPE4": "arranger",
        "TEXT": "lyricist",
        "TCOM": "composer",
        "TCON": "genre",
        "TENC": "encodedby",
        "TALB": "album",
        "TRCK": "tracknumber",
        "TPOS": "discnumber",
        "TSRC": "isrc",
        "TCOP": "copyright",
        "TPUB": "organization",
        "TSST": "part",
        "TOLY": "author",
        "TBPM": "bpm",
        "TDRC": "date",
        "TDOR": "originaldate",
        "TOAL": "originalalbum",
        "TOPE": "originalartist",
        "WOAR": "website",
        }

def get_tag(id3, t):
    """
        Reads a specific id3 tag from the file
    """
    if not id3.has_key(t): return [] 
    field = id3.getall(t)

    ret = []
    if t == 'TDRC' or t == 'TDOR': # values are ID3TimeStamps
        for value in field:
            ret.extend([unicode(x) for x in value.text])
    else:
        for value in field:
            try:
                ret.extend([unicode(x.replace('\n','').replace('\r','')) \
                    for x in value.text])
            except:
                common.log("Can't parse ID3 field")
                common.log_exception()
    return ret

def write_tag(tr):
    try:
        id3 = mutagen.id3.ID3(tr.get_loc_for_io())
    except mutagen.id3.ID3NoHeaderError:
        id3 = mutagen.id3.ID3()

    for id3name, key in IDS.items():
        id3.delall(id3name)

    for k, v in IDS.iteritems():
        if tr.tags[v]:
            try:
                frame = mutagen.id3.Frames[k](encoding=3,
                    text = tr[v])
                id3.loaded_frame(frame)
            except:
                common.log_exception()

    id3.save(tr.io_loc)    

def can_change(tag):
    return tag in IDS.values()

def is_multi():
    return True

def fill_tag_from_path(tr):
    try:
        info = mutagen.mp3.MP3(tr.get_loc_for_io())
    except:
        #common.log_exception()
        common.log("Couldn't read tags from file: " + tr.get_loc())
        return

    tr['length'] = info.info.length
    tr['bitrate'] = info.info.bitrate

    try:    
        id3 = mutagen.id3.ID3(tr.get_loc_for_io())

        for id3_tag, tag in IDS.iteritems():
            tr[tag] = get_tag(id3, id3_tag)
            
    except OverflowError:
        pass
    except mutagen.id3.ID3NoHeaderError:
        pass
    except IOError:
        pass
    except:
        common.log_exception()
