<div class="markdown-body">  

## 이진탐색
![백준 수 찾기](https://user-images.githubusercontent.com/109803585/235814459-47c3e8ae-3d57-49ab-bb44-17566fb471d5.PNG)

### 이진 탐색을 위한 공식

- st: 시작 인덱스
- ed: 끝 인덱스
- target: 탐색 대상 숫자

```
def search(st, en, target):
    if st == en:
        // Logic...
        return

    mid = (st + en) // 2
    if nums[mid] < target:
        search(mid + 1, en, target)
    else:
        search(st, mid, target)
```  
<br>  

### 이진탐색에서의 문제 접근 방법  

- 처음 아이디어: for문으로 각각의 구성요소를 대상으로 해당 수가 존재하는지 확인.
- 처음 시간복잡도
    - for문으로 전체를 M개의 수를 순회한다.
    - for문으로 N개의 리스트를 순회한다.
    - 결과적으로 O(M * N) 이므로 시간초과(1e^10 > 2억개)
- 아이디어
    - 연속하다는 특징이 있는가? ==> 투포인터
    - 정렬해서 순차적으로 확인이 가능한가? ==> 이진탐색

- 이진탐색일 경우의 시간복잡도: O((N+M)lgN)
    - N개의 수 정렬: O(N*lgN)
    - M개의 수 이진탐색: O(M*lgN)  
<br>  

### 해당 문제의 접근방법  

- 아이디어
    - N개의 리스트에서 M개의 리스트 요소를 꺼내서 이진탐색으로 찾기

- 시간복잡도
    - N개의 리스트 정렬(sort) => O(NlgN)
    - M개를 for문을 통해 N개 리스트에 있는지 확인 => O(M * lgN)
    - 총합 : O((N+M)lgN) < 2억개!! ==> 가능.

- 자료구조
    - N개의 숫자 ==> int[]
- M개의 숫자 ==> int[]  
<br>  

### 소스코드  

```
import sys
input = sys.stdin.readline

N=int(input())
n_list=list(map(int, input().split()))
n_list.sort()

M=int(input())
m_list=list(map(int, input().split()))


def solve(st,ed,target):
    if st==ed:
        if n_list[st]==target:
            print( 1 )
        else:
            print( 0 )
        return
    
    mid = (st + ed) // 2
    if n_list[mid] < target:
        solve(mid + 1, ed, target)
    else:
        solve(st, mid, target)

for number in m_list:
    solve(0, N-1, number)
```
</div>
