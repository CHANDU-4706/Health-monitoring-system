import os

if __name__ == '__main__':
    files = os.listdir()
    files = [x for x in files if x.endswith('.json')]
    fw = open('data.csv', 'w', (500*1024*1024))   # SET BUFFER SIZE
    fw.write('service,timestamp,CPU,total_ram,free_ram,total_disk,free_disk')
    for file in files:
        fr = open(file, 'r' , (200*1024*1024))    # SET BUFFER SIZE
        words = fr.read().split()
        i = 1
        while i < len(words):
            fw.write('\n')
            word = words[i]
            service = word[1:-2]
            i += 2
            word = words[i]
            timestamp = word[0:-1]
            i += 2
            word = words[i]
            CPU = word[:-1]
            i += 3
            word = words[i]
            total_ram = word[:-1]
            i += 2
            word = words[i]
            free_ram = word[:-2]
            i += 3
            word = words[i]
            total_disk = word[:-1]
            i += 2
            word = words[i]
            i += 1
            if i >= len(words):
                free_disk = word[:-2]
            else:
                free_disk = word[:-17]
            fw.write(f'{service},{timestamp},{CPU},{total_ram},{free_ram},{total_disk},{free_disk}')
        fr.close()
    fw.close()
