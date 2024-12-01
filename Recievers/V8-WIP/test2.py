# see if i can change NP without init
# sayHi takes np, c from test.py invokationg, then passes it to jj(np, c) this works but it always has to get passed around.: works
# np2, c2 can be created globally and sayHi can assisn np1, c1 to np, c: works
# or sayHi takes np1, c1 and assigns it to global np, c right away. and jj has access to np, c globally: works

global np, c

def sayHi(np1, c1, s):
    global np,  c
    np = np1
    c = c1
    
    for _ in range(3):
        #np.set_neo(c["blue"])
        np.setNeo(c['white'])
        print('Hi')
        s(.4)
        np.setNeo(np.green)
        s(.3)
    jj()
    
    
def jj():
    print('jj')
    np.setNeo(np.red)

    
#sayHi()