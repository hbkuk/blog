<div class="markdown-body">  

## 나무 자르기  

![나무자르기](https://user-images.githubusercontent.com/109803585/236104309-ceab939a-7680-47c5-87bb-60fbaa99a448.PNG)

### 아이디어
- 완전 탐색할 경우 `시간복잡도는 O(N*N)`, 10^6 * 10^6 이므로, 시간초과! 
- **mid를 기준으로 전체 나무를 자른다.**
- 이때, **start 지점이 end 지점과 같아지거나 클때까지 반복**
    - 자른 나무의 총길이(SUM) > 가져가야하는 길이(M)
        - start는 `mid`가 된다.
        - 마치, **최소 높이로 선정**하는 흐름이다.
    - 자른 나무의 총길이(SUM) < 가져가야하는 길이(M)
        - end는 `(mid - 1)`가 된다.
        - 마치, 이 높이는 **터무니 없으니 해당 길이는 제외한다는 흐름**이다.  


### 시간 복잡도
- 해당 문제에서는 **정렬은 없어도 된다.**
- 이진 탐색이므로, 시간복잡도는 **O(N*lgN)**
- O(10^6 * lg10^6) -> 10^6 * 20 -> 2*10^7 < 2억개 => 이진탐색 가능  

### 자료구조
- 나무 리스트 int[]  

### 소스코드
```
import sys
input = sys.stdin.readline

N, M = map(int, input().split())
trees = list(map(int, input().split()))

st = 0
ed = max(trees)

while(st < ed):
    mid = (st + ed) // 2 + 1

    sum = 0
    for tree in trees:
        if tree > mid:
            sum += (tree - mid)
    
    if sum >= M:
        st = mid
    else:
        ed = mid - 1

print( st )
```
</div>