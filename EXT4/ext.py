import sys
import math

def superblock(f):
    f.seek(1024)
    sb = f.read(1024)
    if int.from_bytes(sb[56:58],'little') != 0xEF53:
        print(f"ext 포맷이 아님.")
        sys.exit(-1)
    log_block_size = int.from_bytes(sb[24:28],'little')
    if log_block_size == 0:
        block_size = 1024
    elif log_block_size == 1:
        block_size = 2048
    elif log_block_size == 2:
        block_size = 4096
        
    inode_per_group = int.from_bytes(sb[40:44],'little')
    if int.from_bytes(sb[88:90],'little') == 256:
        inode_structure_size = 256
    else:
        inode_structure_size = 128
    
    if int.from_bytes(sb[254:256],'little') == 0:
        gdt_entry_size = 32
    else:
        gdt_entry_size = int.from_bytes(sb[254:256],'little')
    
    if block_size == 1024:
        gdt_loc = 2
    else: 
        gdt_loc = 1
        
    total_indoes = int.from_bytes(sb[0:4],'little')
    incodes_per_group = int.from_bytes(sb[40:44],'little')
    block_group_count = math.ceil(total_indoes / incodes_per_group)
    
    block_per_group = int.from_bytes(sb[32:36],'little')
    
    return {
        "block_size": block_size,
        "inode_per_group": inode_per_group,
        "inode_structure_size": inode_structure_size,
        "gdt_entry_size": gdt_entry_size,
        "gdt_loc": gdt_loc,
        "block_group_count": block_group_count,
        "block_per_group": block_per_group
    }

def start_block_group_loc(sb_data, n):
    return sb_data['block_per_group'] * sb_data['block_size'] * n

def n_gdt(sb_data, n):
    return sb_data['gdt_entry_size'] * n


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("두개의 인자가 필요합니다.")
        print("ex) python3 ext.py  ext4.dd")
        sys.exit(-1)
    
    file = sys.argv[1]

    with open(file, 'rb') as f:
        sb_data=superblock(f)
        
        gdt_block_count = math.ceil(sb_data['gdt_entry_size']*sb_data['block_group_count'] / sb_data['block_size'])
        root_dir_block_group = start_block_group_loc(sb_data, 0)
        
        gdt_offset = sb_data['gdt_loc'] * sb_data['block_size']
        f.seek(gdt_offset)
        gdt_entry = f.read(sb_data['gdt_entry_size'])
        inode_table_start_block = int.from_bytes(gdt_entry[8:12], 'little')
        
        start_ino = 1
        ext4_root_ino = 2
        root_inode_index = ext4_root_ino - start_ino
        inode_offset_in_table = root_inode_index * sb_data['inode_structure_size']
        
        root_inode_offset = (inode_table_start_block * sb_data['block_size']) + inode_offset_in_table
        f.seek(root_inode_offset)
        inode_data = f.read(sb_data['inode_structure_size'])
        
        inode_flags = int.from_bytes(inode_data[32:36], 'little')
        use_extents = (inode_flags & 0x80000) != 0
        
        data_blocks = []
        if use_extents:
            magic = int.from_bytes(inode_data[40:42], 'little')
            if magic == 0xF30A:
                ex_entry_count = int.from_bytes(inode_data[42:44], 'little')
                for i in range(ex_entry_count):
                    offset = 40 + 12 + (i * 12)
                    entry_data = inode_data[offset:offset+12]
                    
                    ee_len = int.from_bytes(entry_data[4:6], 'little')
                    ee_start_hi = int.from_bytes(entry_data[6:8], 'little')
                    ee_start_lo = int.from_bytes(entry_data[8:12], 'little')
                    start_block = (ee_start_hi << 32) + ee_start_lo
                    
                    for j in range(ee_len):
                        data_blocks.append(start_block + j)
        else:
            for i in range(12):
                offset = 40 + (i * 4)
                block_num = int.from_bytes(inode_data[offset:offset+4], 'little')
                if block_num != 0:
                    data_blocks.append(block_num)
                    
        for block_num in data_blocks:
            block_offset = block_num * sb_data['block_size']
            f.seek(block_offset)
            block_data = f.read(sb_data['block_size'])
            
            cursor = 0
            while cursor < sb_data['block_size']:
                inode = int.from_bytes(block_data[cursor:cursor+4], 'little')
                record_length = int.from_bytes(block_data[cursor+4:cursor+6], 'little')
                
                if record_length == 0: break
                
                if inode != 0:
                    name_len = int.from_bytes(block_data[cursor+6:cursor+7], 'little')
                    name = block_data[cursor+8:cursor+8+name_len].decode('utf-8')
                    print(f"{name} {inode}")
                
                cursor += record_length
                
                
"""
log_block_size => 2
block_size = 4096

inode_per_group = 512
inode_structure_size = 256
gdt_entry_size  = 32
gdt_loc = 1
total_indoes = 65536
block_group_count = 2048
block_per_group = 32

gdt_block_count = 16
root_dir_block_group = 0
gdt_offset = 4096

inode_table_start_block = 81
root_inode_index = 1
inode_offset_in_table = 256
root_inode_offset = 332,032

inode_flags = 0x80000
use_extents = 1

magic = 0xF30A
ex_entry_count = 1
offset = 62+12~144
entry_data = 
ee_len = 2
ee_start_hi = 0
ee_start_lo = 4177
start_block = 4177

block_offset = 4177*4096 = 17,108,992
"""