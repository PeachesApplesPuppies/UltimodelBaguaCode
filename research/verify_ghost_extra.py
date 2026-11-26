from reproduce_unity import kernel
import numpy as np
from scipy.optimize import brentq
from scipy.integrate import quad
import mpmath as mp
H=kernel(480,2,10)
roots=[14.1347251417347,21.0220396387716]
def motion(t,r):
    x=brentq(lambda x:H(t,x),2*r-2,2*r+2,xtol=1e-11)
    v=H(t,x,2)/H(t,x,1)
    acc=(-H(t,x,4)+2*H(t,x,3)*v-H(t,x,2)*v*v)/H(t,x,1)
    return x/2,v/2,acc/2
initial=[motion(0,r) for r in roots]; g0=initial[1][0]-initial[0][0]
def p(t): return (motion(t,roots[1])[0]-motion(t,roots[0])[0])/g0
def pdd(t): return (motion(t,roots[1])[2]-motion(t,roots[0])[2])/g0
print('position, velocity, acceleration',initial,'Pdd(0)',pdd(0))
for t in [.25,.5]:
    average=(p(t)+p(-t))/2
    correction=(quad(lambda v:(t-abs(v))*pdd(v),-t,0,epsabs=1e-10)[0]+quad(lambda v:(t-abs(v))*pdd(v),0,t,epsabs=1e-10)[0])/2
    print('ghost',t,'average',average,'correction',correction,'reconstructed',average-correction)
# Synthetic off-axis quartet polynomial. Numerical Jensen test for normalized transformed polynomial.
mp.mp.dps=40
d=mp.mpf('.2'); t=mp.mpf('14.1347251417347'); roots_s=[mp.mpc(mp.mpf('.5')+a*d,b*t) for a in [-1,1] for b in [-1,1]]
ws=[1-1/s for s in roots_s]
# use a smaller synthetic t to keep zeros well separated from integration boundary
roots_s2=[mp.mpc(mp.mpf('.5')+a*d,b*mp.mpf('1')) for a in [-1,1] for b in [-1,1]]
ws2=[1-1/s for s in roots_s2]
def f(w): return mp.fprod(1-w/a for a in ws2)
r=mp.mpf('.95')
I=mp.quad(lambda th:mp.log(abs(f(r*mp.exp(1j*th)))),[2*mp.pi*j/128 for j in range(129)])/(2*mp.pi)
J=sum(mp.log(r/abs(a)) for a in ws2 if abs(a)<r)
print('synthetic Jensen',mp.nstr(I,24),mp.nstr(J,24),'difference',mp.nstr(abs(I-J),5))
