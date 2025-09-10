import sys
file_syste_type = {5 : 'Extended Partition', 7: 'NTFS', 12 : 'FAT32'}

def EP_read_data(f, offset):
    f.seek(offset, 0)
    read = f.read(16)
    file_type  = check_filetype(read)
    start = int.from_bytes(read[8:12], byteorder='little')
    size = int.from_bytes(read[12:16], byteorder='little')
    return [file_type, start, size]

def ebr_seek(f, base):
    next_ebr = 0
    
    while True:
        ebr_addr = base + next_ebr
        file_type, start, size = EP_read_data(f, (base + next_ebr)*512+446)
        abs_start = ebr_addr + start
        buf.append([file_type, abs_start, size])

        f.seek((base + next_ebr) * 512+446+16, 0)
        next_read = f.read(16)
        next_ebr = int.from_bytes(next_read[8:12], byteorder='little')
        if next_ebr == 0:
            break

def check_filetype(read):
    global error_check
    file_type = file_syste_type.get(int(read[4:5].hex()))
    if file_type is None and error_check == False:
        print(f"FAT32 및 NTFS만 지원합니다. -> 나머지는 None 출력.")
        error_check = True
        return "None"
    return file_type

if __name__  == "__main__":
    if len(sys.argv) != 2:
        print("한개의 파일 인자가 필요합니다.")
        sys.exit(-1)
    file = sys.argv[1]

    buf = []
    error_check = False
    
    with open(file, 'rb') as f:
        f.seek(446, 0)
        for i in range(4):
            read = f.read(16)
            file_type  = check_filetype(read)
            start = int.from_bytes(read[8:12], byteorder='little')
            size = int.from_bytes(read[12:16], byteorder='little')
            buf.append([file_type, start, size])

        if buf[-1][0] == "Extended Partition":
            buf.pop()
            ebr_seek(f, start)

        for i in range(len(buf)):
            print(f"{buf[i][0]} {buf[i][1]:8d} {buf[i][2]:8d}")