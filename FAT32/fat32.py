import sys

cluster = []

def init(f):
    f.seek(11, 0)
    BytePerSector = int.from_bytes(f.read(2), byteorder='little')
    SectorPerCluster = int.from_bytes(f.read(1), byteorder='little')
    ReservedSectorCount = int.from_bytes(f.read(2), byteorder='little')
    NumberOfFats = int.from_bytes(f.read(1), byteorder='little')
    f.seek(36,0)
    Fat32Size = int.from_bytes(f.read(4), byteorder='little')
    f.seek(44,0)
    RootDirCluster = int.from_bytes(f.read(4), byteorder='little')
    First_data_sector = ReservedSectorCount + Fat32Size * NumberOfFats
    return [BytePerSector, SectorPerCluster, ReservedSectorCount, NumberOfFats, Fat32Size, RootDirCluster, First_data_sector]

def linkedCluster(f, currentCluster, fat_start):
    while(True):
        cluster.append(currentCluster)
        fat_entry = fat_start + (currentCluster * 4)
        f.seek(fat_entry, 0)
        fat_table = f.read(4)
        next_cluster = int.from_bytes(fat_table, byteorder='little')

        if next_cluster >= 0x0FFFFFF8:
            break
        else:
            currentCluster = next_cluster

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("두개의 인자가 필요합니다.")
        print("ex) python3 fat32.py fat32.dd 22")
        sys.exit(-1)
    file = sys.argv[1]

    with open(file, 'rb') as f:
        init_l = init(f)
        BytePerSector = init_l[0]
        ReservedSectorCount = init_l[2]
        currentCluster = int(sys.argv[2])
        fat_start = ReservedSectorCount * BytePerSector
        linkedCluster(f, currentCluster, fat_start)

    for i in cluster:
        if i != cluster[-1]:
            print(f"{i}", end = ",")
        else:
            print(i)