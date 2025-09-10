import sys
buf = []

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("한개의 파일 인자가 필요합니다.")
        sys.exit(-1)
    file = sys.argv[1]

    with open(file, 'rb') as f:
        f.seek(512*2, 0)
        while True:
            read = f.read(128)
            if read == b'\x00' * 128:
                break
            guid = read[0:16].hex().upper()
            start = int.from_bytes(read[32:40], byteorder='little')
            end = int.from_bytes(read[40:48], byteorder='little')
            size = (end - start + 1) * 512
            buf.append([guid, start, size])
            
        for i in range(len(buf)):
            print(f"{buf[i][0]} {buf[i][1]:8d} {buf[i][2]:8d}")






            """
{GUID} {FileSystem Type} {real Offset Sector} {size}
"""
import sys
buf = []
"""
def scan_type(f, start):
    save = f.tell()
    f.seek(start*512 + 3, 0)
    Filesystem_Type = f.read(4)
    f.seek(save, 0)
    return Filesystem_Type.upper() 
"""

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("한개의 파일 인자가 필요합니다.")
        sys.exit(-1)
    file = sys.argv[1]

    with open(file, 'rb') as f:
        f.seek(512*2, 0)
        while True:
            read = f.read(128)
            if read == b'\x00' * 128:
                break
            guid = read[0:16].hex().upper()
            start = int.from_bytes(read[32:40], byteorder='little')
            end = int.from_bytes(read[40:48], byteorder='little')
            #filesystem_type = scan_type(f, start)
            size = (end - start + 1) * 512
            #buf.append([guid, filesystem_type, start, size])
            buf.append([guid, start, size])
            
        for i in range(len(buf)):
            #print(f"{buf[i][0]} {buf[i][1]} {buf[i][2]:8d} {buf[i][3]:8d}")
            print(f"{buf[i][0]} {buf[i][1]:8d} {buf[i][2]:8d}")

            """
            import sys
file_syste_type = {5 : 'Extended Partition', 7: 'NTFS', 12 : 'FAT32'}

def read_data(f, offset):
    f.seek(offset, 0)
    read = f.read(16)
    file_type  = file_syste_type[int(read[4:5].hex())]
    start = int.from_bytes(read[8:12], byteorder='little')
    size = int.from_bytes(read[12:16], byteorder='little')
    return [file_type, start, size]

def ebr_seek(f, base):
    next_ebr = 0
    
    while True:
        ebr_addr = base + next_ebr
        f.seek((base + next_ebr) * 512 + 446, 0)
        read = f.read(16)
        file_type, start, size = read_data(f, (base + next_ebr)*512+446)
        abs_start = ebr_addr + start
        buf.append([file_type, abs_start, size])

        f.seek((base + next_ebr) * 512+446+16, 0)
        next_read = f.read(16)
        next_ebr = int.from_bytes(next_read[8:12], byteorder='little')
        if next_ebr == 0:
            break
    return 0

if __name__  == "__main__":
    if len(sys.argv) != 2:
        print("한개의 파일 인자가 필요합니다.")
        sys.exit(-1)
    file = sys.argv[1]

    buf = []
    
    with open(file, 'rb') as f:
        f.seek(446, 0)
        for i in range(4):
            read = f.read(16)
            file_type  = file_syste_type[int(read[4:5].hex())]
            start = int.from_bytes(read[8:12], byteorder='little')
            size = int.from_bytes(read[12:16], byteorder='little')
            buf.append([file_type, start, size])

        if buf[-1][0] == "Extended Partition":
            buf.pop()
            ebr_seek(f, start)

        for i in range(len(buf)):
            print(f"{buf[i][0]} {buf[i][1]:8d} {buf[i][2]:8d}")
            """