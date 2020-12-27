class Solution:
    def isIsomorphic(self, s: str, t: str) -> bool:
        if len(s)!=len(t):
            return False
        d={}
        new_s=""
        for i in range(len(s)):
            if not d.get(s[i]):
                d[s[i]]=t[i]
        c=set()
        for i in d:
            c.add(d[i])
        if len(c)!=len(d):
            return False
        for i in s:
            new_s+=d[i]
        print(new_s)
        return new_s==t

s="ab"
t="aa"
a=Solution()
b=a.isIsomorphic(s,t)
print(b)