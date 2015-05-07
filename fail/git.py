from symbolic.args import *

@symbolic(a=0xdeaddeaddeaddead,b=0xbeefbeefbeefbeef)
def git(a,b):
    i=0;
    passkeyn=[a,b]

    expandedkey=[]
    while i<6:
#    while i<2:  # WORKS
        expandedkey=expandedkey+passkeyn
        i=i+1
        v1=passkeyn[0]
        v2=passkeyn[1]
        v3=(v1>>0x30)|(((v1>>0x20)&0xffff)<<0x10)|(((v1>>0x10)&0xffff)<<0x20)|((v1&0xffff)<<0x30)
        v4=(v2>>0x30)|(((v2>>0x20)&0xffff)<<0x10)|(((v2>>0x10)&0xffff)<<0x20)|((v2&0xffff)<<0x30)
        v5 = ((v4 & 0xFFFFFF8000000000) >> 39) | ((v3 << 25)&0xffffffffffffffff);
        v6 = ((v3 & 0xFFFFFF8000000000) >> 39) | ((v4 << 25)&0xffffffffffffffff);
        v1=(v5>>0x30)|(((v5>>0x20)&0xffff)<<0x10)|(((v5>>0x10)&0xffff)<<0x20)|(((v4 & 0xFFFFFF8000000000) >> 39)<<0x30)
        v2=(v6>>0x30)|(((v6>>32)&0xffff)<<0x10)|(((v6>>0x10)&0xffff)<<0x20)|(((v3 & 0xFFFFFF8000000000) >> 39)<<0x30)
        passkeyn=[v1,v2]
    
    expandedkey=expandedkey+passkeyn
    
    print(expandedkey)
    if expandedkey==[16045725885737590445, 13758425323549998831, 7044313620519854103485, 8215411798635391606653, 8245388070021240879798, 3384596836810669685695, 9287860625795901259255, 4527376222128629444341, 4093654381503457390331, 4647353382867023162077, 8665057901351565392853, 8816957627389395711965, 6783497306152038280055, 9291067819851303074799]:
#    WORKS
#    if expandedkey==[16045725885737590445, 13758425323549998831, 7044313620519854103485, 8215411798635391606653, 8245388070021240879798, 3384596836810669685695]:
        print("HERE")
        return 1
    else:
        print("THERE")
        return 2

if __name__ == "__main__":
    git(0xdeaddeaddeaddead,0xbeefbeefbeefbeef)
