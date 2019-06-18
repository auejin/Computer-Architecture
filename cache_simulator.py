"""
Cache Simulator
Author : github.com/auejin

how to Run : $ python3 ./cache_simulator.py <-c capacity> <-a associativity> <-b block_size> <input file>
"""

import sys
import math

# Cache Policy #
# write-back : 모든 block에는 dirty bit가 존재
# Least Recently Used : 블록 교체 정책 (block별로 사용 순서 기록해둬야)

class UnitBlock:
    def __init__(self):
        self.tag = 0
        self.valid = 0
        self.dirty = 0
        self.LRU = 0 # 0 when empty, highest == 가장 늦게 사용 == remove target
        self.data = 0 # can contain multiple words

class CacheSimulator : # This emulator is based on single cycle design
    def __init__(self):
        self.capacity = 4       # 캐시 용량(KB) : 4~1024KB # 8B=1word 여러개를 저장하는 Data단의 크기
        self.associativity = 1  # 캐시 연관정도 : 1~16 (way의 수)
        self.block_size = 16    # 블록 1개 크기(B) : 16~128B (B=8bit)

        self._read_acc_count = 0
        self._read_miss_count = 0
        self._write_acc_count = 0
        self._write_miss_count = 0
        self._clean_eviction_count = 0
        self._dirty_eviction_count = 0

        self._set_count = 0
        self.cache = [[]]
        self.memory = {}
    
    def check_sum(self):
        checksum = 0
        for i in range(self.associativity) :
            for j in range(self._set_count):
                if self.cache[i][j].valid :
                    tag = self.cache[i][j].tag
                    dirty = self.cache[i][j].dirty
                    checksum = checksum ^ ( ( (tag^j) << 1 ) | dirty )
        return checksum


    def _ln2(self, x):
        return math.ceil(math.log2(x))

    def init_cache(self, capacity, associativity, block_size):
        self.capacity = capacity
        self.associativity = associativity
        self.block_size = block_size
        
        self._set_count = capacity * 1024 // block_size // associativity
        self.cache = [] # self.associativity*[self._set_count*[UnitBlock()]]는 unitblock 하나가 복사됨
        for i in range(self.associativity) : 
            way = []
            for j in range(self._set_count) : 
                way.append(UnitBlock())
            self.cache.append(way)

    def _split_addr(self, addr_str):
        # 트레이스 파일은 16진수로 표기된 64비트 정수입니다. 
        # 그러므로 8바이트 단위의 워드를 사용하시는 것이 맞습니다.
        addr_bin = bin(int(addr_str,0))[2:]

        offset_len = -1 * self._ln2(self.block_size)
        index_len = -1 * self._ln2(self._set_count)

        block_offset = addr_bin[offset_len:]
        index = addr_bin[offset_len+index_len:offset_len]
        tag = addr_bin[:offset_len+index_len]

        return int('0b'+block_offset,0), int('0b'+index,0), int('0b'+tag,0)
    
    def _LRU_update(self,index, is_hit, hit_way):        
        if is_hit :
            max_way = hit_way
        else :
            LRUs = [self.cache[i][index].LRU for i in range(self.associativity)]
            max_way, max_LRU = LRUs.index(max(LRUs)), max(LRUs)
        # hit 된거 없으면 max_way번째 way의 index번째 block을 업데이트
        
        for i in range(self.associativity) : # 최신꺼 0, 이후꺼 +1
            self.cache[i][index].LRU += 1        
        self.cache[max_way][index].LRU = 0

        return max_way

    def _check_hit(self, block_offset, index, tag):
        for i in range(self.associativity) :
            if self.cache[i][index].valid and self.cache[i][index].tag == tag :
                return True, i
        return False, None

    def print_cache_line(self, index):
        print("dirty : ",end="")
        for i in range(self.associativity) : 
            print(self.cache[i][index].dirty, end=", ")
        print()
        print("LRU   : ",end="")
        for i in range(self.associativity) : 
            print(self.cache[i][index].LRU, end=", ")
        print()
        print("valid : ",end="")
        for i in range(self.associativity) : 
            print(self.cache[i][index].valid, end=", ")
        print()
        print()

    def read_trace_files(self, file_name):
        f = open(file_name, 'r')

        while True:
            line = f.readline()
            if not line: break
            rw, physical_addr = line.split()

            block_offset, index, tag = self._split_addr(physical_addr)

            is_hit, hit_way = self._check_hit(block_offset, index, tag)
            max_way = self._LRU_update(index, is_hit, hit_way)

            if rw == "R" :
                self._read_acc_count += 1
                if not is_hit :
                    self._read_miss_count += 1
                    # eviction(replace 필요)시 내쫒고 dirty=0으로 새로 읽어와 replace
                    if self.cache[max_way][index].valid > 0 : # eviction == 덮어쓰려는 위치에 데이터 존재 TODO : 전부 valid할때까지 dirty 나오면 안됨
                        if self.cache[max_way][index].dirty > 0 : # dirty = 덮어씌워진 block의 cache가 mem에 적용이 안되어 dirty=1인경우
                            self._dirty_eviction_count += 1
                        else :
                            self._clean_eviction_count += 1
                    
                    self.cache[max_way][index].dirty = 0
                    self.cache[max_way][index].tag = tag
                    self.cache[max_way][index].valid = 1

                else :
                    # TODO : evictions합이 원래랑 같으니까 valid는 문제 없고 dirty가 문제인듯
                    # dirty여부 관계 없이 cache내 값을 읽으면 된다. eviction검사 필요 X
                    pass
                
            elif rw == "W" :
                self._write_acc_count += 1
                if not is_hit :
                    self._write_miss_count += 1
                    # TODO : 새로 읽어와서 덮어 씌워야 한다.
                    if self.cache[max_way][index].valid > 0 :
                        if self.cache[max_way][index].dirty > 0 :
                            #print("dirty!\n\n")
                            self._dirty_eviction_count += 1
                            pass
                        else :
                            self._clean_eviction_count += 1
                            pass
                    self.cache[max_way][index].dirty = 1
                    self.cache[max_way][index].tag = tag
                    self.cache[max_way][index].valid = 1
                else :
                    # TODO : cache에 저장된 내용 그대로 쓰면 된다. dirty = 1
                    # hit된 부분에 그대로 값만 바꿔주면 되므로 mem접근 없이 dirty=1후 값만 없뎃함
                    # 즉, eviction검사가 필요 없다.
                    self.cache[hit_way][index].dirty = 1
                    self.cache[hit_way][index].valid = 1
        
        f.close()
    
    def write_result(self, file_name):
        name = f"{file_name.split('.')[0]}_{self.capacity}_{self.associativity}_{self.block_size}"
        f = open(name + ".out", 'w')
        wline = lambda s : print(s) or f.write(s + '\n')
        
        wline("-- General Stats --")
        wline(f"Capacity: {self.capacity}")
        wline(f"Way: {self.associativity}")
        wline(f"Block size: {self.block_size}")
        wline(f"Total accesses: {self._read_acc_count + self._write_acc_count}")
        wline(f"Read accesses: {self._read_acc_count}")
        wline(f"Write accesses: {self._write_acc_count}")
        wline(f"Read misses: {self._read_miss_count}")
        wline(f"Write misses: {self._write_miss_count}")
        wline(f"Read miss rate: {self._read_miss_count / self._read_acc_count * 100}%")
        wline(f"Write miss rate: {self._write_miss_count / self._write_acc_count * 100}%")
        wline(f"Clean evictions: {self._clean_eviction_count}")
        wline(f"Dirty evictions: {self._dirty_eviction_count}")
        wline(f"Checksum: {hex(self.check_sum())}")

        f.close()
    # end of class CacheSimulator() #



if __name__ == "__main__":
    argv = sys.argv
    cache = CacheSimulator()

    if "-c" in argv and "-a" in argv and "-b" in argv:
        for s in "cab" :
            arg_value = int(argv[argv.index("-"+s)+1],0)
            if math.log2(arg_value) % 1 != 0 :
                raise ValueError(f"parameter -{s} must be power of two.")
        
        capacity = int(argv[argv.index("-c")+1],0)
        associativity = int(argv[argv.index("-a")+1],0)
        block_size = int(argv[argv.index("-b")+1],0)
        
        cache.init_cache(capacity, associativity, block_size)
        
        cache.read_trace_files(argv[-1])
        cache.write_result(argv[-1])
    else :
        raise ValueError("all three parameters (-c, -a, -b) must be defined.")

