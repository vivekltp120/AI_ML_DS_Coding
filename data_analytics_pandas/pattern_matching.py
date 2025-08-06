#rabin carp pattern matching algorithm

hashmap=[]
def get_256_character():
    for i in range(256):
        hashmap.append(chr(i))
    print(hashmap)
    print('length of hashmap-'+str(len(hashmap)))
    print('back to ascii')
    for x in hashmap:
        print(ord(x))
        print(isinstance(ord(x),int))


def pattern_hashvalue(pattern):
    plen=len(pattern)
    preverse=pattern[::-1]
    hashvalue=0
    for i in range(plen):
        hashvalue+=ord(preverse[i])*(256**i)

    # print(hashvalue)
    return hashvalue

def rolling_hashvalue(predict_str,plen):
    pass


def rabin_carp(pattern,source_str):
    pattern_hash_value=pattern_hashvalue(pattern)
    plen=len(pattern)
    prev_hash_value=0
    if len(source_str)>plen:
        prev_hash_value=pattern_hashvalue(source_str[:plen])
        print('pre_hash_value-'+str(prev_hash_value))
        if pattern_hash_value==prev_hash_value:
            print(str(0)+' '+str(plen-1))
            # return 0,plen-1
    else:
        print('Source string have no enough length')

    for i in range(1,len(source_str)-plen+1):
        new_hash=(prev_hash_value-(ord(source_str[i-1])*(256**(plen-1))))*256+ord(source_str[i+plen-1])
        if pattern_hash_value==new_hash:
            print(str(i)+' '+str(i+plen-1))
            # return i,i+plen

        prev_hash_value=new_hash

if __name__=="__main__":
    # get_256_character()
    # pattern_hashvalue('fdsfjjfjfjsdjfk')
    rabin_carp('abc','abcabcabcabcabc')
