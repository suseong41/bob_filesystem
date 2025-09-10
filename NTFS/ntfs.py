import sys

diskAssign = []

def init(f):
    init_t = f.read(512)
    BytePerSector = int.from_bytes(init_t[11:13], 'little')
    SectorPerCluster = int.from_bytes(init_t[13:14], 'little')
    mftStartCluster = int.from_bytes(init_t[48:56], 'little')
    
    clusterSize = BytePerSector * SectorPerCluster
    return clusterSize, mftStartCluster

def findMftRunList(mft0Entry):
    attrOffset = int.from_bytes(mft0Entry[20:22], 'little')
    runListData = None

    while attrOffset < 1024:
        attrType = int.from_bytes(mft0Entry[attrOffset:attrOffset+4], 'little')
        if attrType == 0xFFFFFFFF: break
        
        attrLen = int.from_bytes(mft0Entry[attrOffset+4:attrOffset+8], 'little')
        if attrType == 0x80:
            nonResidentFlag = mft0Entry[attrOffset+8]
            if nonResidentFlag == 1:
                runListOffsetInAttr = int.from_bytes(mft0Entry[attrOffset+32:attrOffset+34], 'little')
                runListStart = attrOffset + runListOffsetInAttr
                runListData = mft0Entry[runListStart:attrOffset+attrLen]
                break
        
        if attrLen == 0: break
        
        attrOffset += attrLen
    
    if not runListData:
        print("error: not found run list")
        sys.exit(-1)


    currentRunOffset = 0
    prevClusterOffset = 0
    
    while True:
        if runListData[currentRunOffset] == 0x00:
            break
        
        FirstRunListByte = runListData[currentRunOffset]
        currentRunOffset += 1
        
        RunLength = FirstRunListByte & 0x0F
        RunOffset = (FirstRunListByte & 0xF0) >> 4
        
        lengthBytes = runListData[currentRunOffset:currentRunOffset+RunLength]
        runLength = int.from_bytes(lengthBytes, 'little')
        currentRunOffset += RunLength
        
        offsetBytes = runListData[currentRunOffset:currentRunOffset+RunOffset]
        runOffset = int.from_bytes(offsetBytes, 'little')
        currentRunOffset += RunOffset
        
        absStartCluster = prevClusterOffset + runOffset
        diskAssign.append([absStartCluster, runLength])
        prevClusterOffset = absStartCluster


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("두개의 인자가 필요합니다.")
        print("ex) python3 ntfs.py  ntfs.dd")
        sys.exit(-1)
    
    file = sys.argv[1]

    with open(file, 'rb') as f:

        clusterSize, mftStartCluster = init(f)

        mftByteOffset = clusterSize * mftStartCluster
        f.seek(mftByteOffset)
        mft0Entry = f.read(1024)
        if mft0Entry[0:4] != b"FILE":
            sys.exit(-1)
        
        findMftRunList(mft0Entry)
            

    clusterCount = sum(size for _, size in diskAssign)
    print(f"{clusterCount}")
    for start, size in diskAssign:
        print(f"{start:<6d} {size:<4d}", end = "")
        
        

"""

BytePerSector = 2
SectorPerCluster = 2048
mftStartCluster = 1AAA
clustersize = 2048 * 2 = 4096

mftByteOffset = 27,959,296

attrOffset = 56
runListData = None

->
attrType = 16
attrLen = 96

attrOffset = 56 + 96
->
attrType = 48
attrLen = 104

attrOffset = 56 + 96 + 104
->
attrType = 80
attrLen = 72

attrOffset = 56 + 96 + 104 = 256

nonResidentFlag = 01

runListOffsetInAttr = 64

runListStart = 320

runListData = 320:372

runListData = 21 40 AA 1A 00 00 00 00
currentRunOffset = 0

prevClusterOffset = 0


FirstRunListByte = 0010 0001
currentRunOffset = 1

RunLength = 1
RunOffset = 2
lengthBytes = 40 = 64

offsetBytes =  AA 1A
runOffset = A = 6826

absStartCluster = 6826

next: 00 00 00 00

"""