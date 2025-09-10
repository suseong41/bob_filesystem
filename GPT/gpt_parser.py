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
            print(f"{buf[i][0]} {buf[i][1]:8d} {buf[i][2]:12d}")