from Constants import connString
import pypyodbc
class VideoDataModel:
    def __init__(self, videoID, author, keywords="", fileSize=0, mediaFormat="", closedCaption="", contentData="", videoFileName="", cloudProviderModel=None, isDownloadedToServer=0, hash="", prevHash=""):
        self.videoID = videoID
        self.author = author
        self.keywords = keywords
        self.fileSize = fileSize
        self.mediaFormat = mediaFormat
        self.closedCaption = closedCaption
        self.contentData = contentData
        self.videoFileName = videoFileName
        self.cloudProviderModel = cloudProviderModel
        self.isDownloadedToServer = isDownloadedToServer
        self.hash=hash
        self.prevHash = prevHash


@staticmethod
def getAllVideoDetails():
    conn3 = pypyodbc.connect(connString, autocommit=True)
    cur3 = conn3.cursor()

    sqlcmd = "SELECT videoID, author, keywords, fileSize, mediaFormat, closedCaption, videoFileName, hash, prevHash FROM VideoDataModel ORDER BY videoID"
    print(sqlcmd)
    cur3.execute(sqlcmd)

    records = []
    while True:
        row = cur3.fetchone()
        if row:

            pmodel = VideoDataModel(row[0], author=row[1], keywords=row[2], fileSize=row[3], mediaFormat=row[4],
                                 closedCaption=row[5], videoFileName=row[6], hash=row[7], prevHash=row[8])
            records.append(pmodel)
        else:
            break
    return records